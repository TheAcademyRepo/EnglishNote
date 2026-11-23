from django.db import transaction
from django.db.models import F
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied, NotFound

from app.roles import UserRole
from app.role_permissions import get_user_role

from .models import ContentItem, ContentReview, ContentVersion
from .serializers import (
    ContentItemSerializer,
    ContentReviewSerializer,
    ContentVersionSerializer,
)


def can_manage_all_content(role):
    return role in [
        UserRole.EDITOR,
        UserRole.ADMINISTRATOR,
        UserRole.SUPER_ADMINISTRATOR,
    ]


def can_publish(role):
    return role in [
        UserRole.AUTHOR,
        UserRole.ADMINISTRATOR,
        UserRole.SUPER_ADMINISTRATOR,
    ]


class ContentListCreateView(generics.ListCreateAPIView):

    serializer_class = ContentItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user = self.request.user
        role = get_user_role(user)

        queryset = ContentItem.objects.select_related(
            "author",
            "category",
            "topic",
            "reviewer",
        )

        if can_manage_all_content(role):
            pass
        else:
            queryset = queryset.filter(author=user)

        status_filter = self.request.query_params.get("status")
        content_type = self.request.query_params.get("type")

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if content_type:
            queryset = queryset.filter(content_type=content_type)

        return queryset

    def perform_create(self, serializer):

        role = get_user_role(self.request.user)

        if role not in [
            UserRole.CONTRIBUTOR,
            UserRole.AUTHOR,
            UserRole.ADMINISTRATOR,
            UserRole.SUPER_ADMINISTRATOR,
        ]:
            raise PermissionDenied(
                "You are not permitted to create content."
            )

        content_type = serializer.validated_data["content_type"]

        if content_type == ContentItem.ContentType.DAILY and not can_publish(role):
            raise PermissionDenied(
                "Only Authors and Administrators can create daily posts."
            )

        if can_publish(role):

            serializer.save(
                author=self.request.user,
                status=ContentItem.Status.PUBLISHED,
                published_at=timezone.now(),
            )

        else:

            serializer.save(
                author=self.request.user,
                status=ContentItem.Status.DRAFT,
                published_at=None,
            )


class PublicContentListView(generics.ListAPIView):

    serializer_class = ContentItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):

        queryset = ContentItem.objects.filter(
            status=ContentItem.Status.PUBLISHED,
            published_at__isnull=False,
            published_at__lte=timezone.now(),
        ).select_related(
            "author",
            "category",
            "topic",
        )

        content_type = self.request.query_params.get("type")
        search = self.request.query_params.get("search")
        category = self.request.query_params.get("category")
        topic = self.request.query_params.get("topic")

        if content_type:
            queryset = queryset.filter(content_type=content_type)

        if search:
            from django.db.models import Q

            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(excerpt__icontains=search)
                | Q(body__icontains=search)
            )

        if category:
            queryset = queryset.filter(category__slug=category)

        if topic:
            queryset = queryset.filter(topic__slug=topic)

        return queryset.distinct()


class ContentDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = ContentItemSerializer
    lookup_field = "slug"

    def get_permissions(self):

        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return [AllowAny()]

        return [IsAuthenticated()]

    def get_queryset(self):

        queryset = ContentItem.objects.select_related(
            "author",
            "category",
            "topic",
        )

        if self.request.method in ["GET", "HEAD", "OPTIONS"]:

            return queryset.filter(
                status=ContentItem.Status.PUBLISHED,
                published_at__isnull=False,
                published_at__lte=timezone.now(),
            )

        role = get_user_role(self.request.user)

        if can_manage_all_content(role):
            return queryset

        return queryset.filter(author=self.request.user)

    def perform_update(self, serializer):

        content = self.get_object()

        role = get_user_role(self.request.user)

        if content.author_id != self.request.user.id and not can_manage_all_content(role):
            raise PermissionDenied(
                "You cannot edit another user's content."
            )

        if content.status == ContentItem.Status.PUBLISHED:

            ContentVersion.objects.create(
                content=content,
                title=content.title,
                body=content.body,
                edited_by=self.request.user,
            )

        # A published item edited by its author must return to review.
        # An editor/admin correction should also require re-approval.
        serializer.save(
            status=ContentItem.Status.DRAFT,
            published_at=None,
            reviewer=None,
        )

    def perform_destroy(self, instance):

        role = get_user_role(self.request.user)

        if instance.author_id != self.request.user.id and role not in [
            UserRole.ADMINISTRATOR,
            UserRole.SUPER_ADMINISTRATOR,
        ]:
            raise PermissionDenied(
                "You cannot delete another user's content."
            )

        instance.delete()


class SubmitContentView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        content = ContentItem.objects.filter(
            pk=pk,
            author=request.user,
        ).first()

        if not content:
            raise NotFound("Content not found.")

        if content.status not in [
            ContentItem.Status.DRAFT,
            ContentItem.Status.REVISION,
            ContentItem.Status.REJECTED,
        ]:
            return Response(
                {"detail": "This content cannot be submitted in its current state."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        content.status = ContentItem.Status.SUBMITTED
        content.review_notes = ""
        content.rejection_reason = ""

        content.save(
            update_fields=[
                "status",
                "review_notes",
                "rejection_reason",
                "updated_at",
            ]
        )

        return Response({
            "detail": "Your content has been submitted for review."
        })


class ReviewContentView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        role = get_user_role(request.user)

        if role not in [
            UserRole.AUTHOR,
            UserRole.EDITOR,
            UserRole.ADMINISTRATOR,
            UserRole.SUPER_ADMINISTRATOR,
        ]:
            raise PermissionDenied(
                "You are not authorized to review content."
            )

        with transaction.atomic():

            content = ContentItem.objects.select_for_update().filter(
                pk=pk
            ).first()

            if not content:
                raise NotFound("Content not found.")

            if content.author_id == request.user.id:
                raise PermissionDenied(
                    "You cannot review your own content."
                )

            if content.status not in [
                ContentItem.Status.SUBMITTED,
                ContentItem.Status.IN_REVIEW,
            ]:
                return Response(
                    {"detail": "This content is not awaiting review."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            decision = request.data.get("decision")
            feedback = request.data.get("feedback", "")

            valid_decisions = [
                ContentReview.Decision.APPROVED,
                ContentReview.Decision.REJECTED,
                ContentReview.Decision.REVISION,
            ]

            if decision not in valid_decisions:
                return Response(
                    {"detail": "Invalid review decision."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if decision == ContentReview.Decision.APPROVED and role == UserRole.EDITOR:

                return Response(
                    {
                        "detail": (
                            "Editors can recommend approval. "
                            "An Author or Administrator must approve publication."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            ContentReview.objects.create(
                content=content,
                reviewer=request.user,
                decision=decision,
                feedback=feedback,
            )

            content.reviewer = request.user

            if decision == ContentReview.Decision.APPROVED:
                content.status = ContentItem.Status.APPROVED
                content.review_notes = feedback

            elif decision == ContentReview.Decision.REJECTED:
                content.status = ContentItem.Status.REJECTED
                content.rejection_reason = feedback

            else:
                content.status = ContentItem.Status.REVISION
                content.review_notes = feedback

            content.save()

        return Response({
            "detail": "Review decision recorded.",
            "status": content.status,
        })


class PublishContentView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        role = get_user_role(request.user)

        if not can_publish(role):
            raise PermissionDenied(
                "You cannot publish content."
            )

        with transaction.atomic():

            content = ContentItem.objects.select_for_update().filter(
                pk=pk
            ).first()

            if not content:
                raise NotFound("Content not found.")

            if role == UserRole.AUTHOR and content.author_id != request.user.id:
                raise PermissionDenied(
                    "Authors can only publish their own content."
                )

            if content.status != ContentItem.Status.APPROVED:
                return Response(
                    {"detail": "Content must be approved before publication."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            content.status = ContentItem.Status.PUBLISHED
            content.published_at = timezone.now()

            content.save(
                update_fields=[
                    "status",
                    "published_at",
                    "updated_at",
                ]
            )

        return Response({
            "detail": "Content published successfully."
        })


class ContentViewCountView(APIView):

    permission_classes = [AllowAny]

    def post(self, request, pk):

        content = ContentItem.objects.filter(
            pk=pk,
            status=ContentItem.Status.PUBLISHED,
            published_at__lte=timezone.now(),
        ).first()

        if not content:
            raise NotFound("Published content not found.")

        session_key = f"content_view_{content.id}"

        if request.session.get(session_key):

            return Response({
                "detail": "View already recorded."
            })

        ContentItem.objects.filter(
            pk=content.id
        ).update(
            views=F("views") + 1
        )

        request.session[session_key] = True

        return Response({
            "detail": "View recorded."
        })


class ContentVersionListView(generics.ListAPIView):

    serializer_class = ContentVersionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        content = ContentItem.objects.filter(
            pk=self.kwargs["pk"]
        ).first()

        if not content:
            return ContentVersion.objects.none()

        role = get_user_role(self.request.user)

        if (
            content.author_id != self.request.user.id
            and role not in [
                UserRole.EDITOR,
                UserRole.ADMINISTRATOR,
                UserRole.SUPER_ADMINISTRATOR,
            ]
        ):
            raise PermissionDenied(
                "You cannot view these content versions."
            )

        return content.versions.select_related("edited_by")

class PublicContentDetailView(generics.RetrieveAPIView):

    serializer_class = ContentItemSerializer

    permission_classes = [AllowAny]

    lookup_field = "slug"

    def get_queryset(self):

        return ContentItem.objects.filter(
            status=ContentItem.Status.PUBLISHED,
            published_at__isnull=False,
            published_at__lte=timezone.now(),
        ).select_related(
            "author",
            "category",
            "topic",
        )
        
        
        
class ContentReviewListView(generics.ListAPIView):

    serializer_class = ContentReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        role = get_user_role(self.request.user)

        if role not in [
            UserRole.AUTHOR,
            UserRole.EDITOR,
            UserRole.ADMINISTRATOR,
            UserRole.SUPER_ADMINISTRATOR,
        ]:
            return ContentReview.objects.none()

        return ContentReview.objects.select_related(
            "content",
            "reviewer",
        )