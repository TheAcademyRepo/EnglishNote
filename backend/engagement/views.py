from django.db import transaction
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import (
    NotFound,
    PermissionDenied,
    ValidationError,
)

from publishing.models import ContentItem

from app.roles import UserRole
from app.role_permissions import get_user_role

from .models import (
    Like,
    Bookmark,
    Share,
    Comment,
    Report,
)

from .serializers import (
    BookmarkSerializer,
    ShareSerializer,
    CommentSerializer,
    ReportSerializer,
)


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_published_content(pk):

    return ContentItem.objects.filter(
        pk=pk,
        status=ContentItem.Status.PUBLISHED,
        published_at__isnull=False,
        published_at__lte=timezone.now(),
    ).first()


def is_moderator(user):

    if not user or not user.is_authenticated:
        return False

    return get_user_role(user) in [
        UserRole.AUTHOR,
        UserRole.EDITOR,
        UserRole.ADMINISTRATOR,
        UserRole.SUPER_ADMINISTRATOR,
    ]


# ==========================================
# LIKE CONTENT
# ==========================================

class LikeToggleView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        content = get_published_content(pk)

        if not content:
            raise NotFound(
                "Published content not found."
            )

        with transaction.atomic():

            like, created = Like.objects.get_or_create(
                user=request.user,
                content=content,
            )

            if not created:

                like.delete()
                liked = False

            else:

                liked = True

        return Response({
            "message": "Like updated successfully.",
            "liked": liked,
            "likes_count": content.likes.count(),
        })


# ==========================================
# BOOKMARK CONTENT
# ==========================================

class BookmarkToggleView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        content = get_published_content(pk)

        if not content:
            raise NotFound(
                "Published content not found."
            )

        with transaction.atomic():

            bookmark, created = Bookmark.objects.get_or_create(
                user=request.user,
                content=content,
            )

            if not created:

                bookmark.delete()
                saved = False

            else:

                saved = True

        return Response({
            "message": "Bookmark updated successfully.",
            "bookmarked": saved,
        })


# ==========================================
# MY BOOKMARKS
# ==========================================

class MyBookmarksView(generics.ListAPIView):

    serializer_class = BookmarkSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return Bookmark.objects.filter(
            user=self.request.user,
            content__status=ContentItem.Status.PUBLISHED,
            content__published_at__lte=timezone.now(),
        ).select_related("content")


# ==========================================
# SHARE CONTENT
# ==========================================

class ShareContentView(APIView):

    permission_classes = [AllowAny]

    def post(self, request, pk):

        content = get_published_content(pk)

        if not content:
            raise NotFound(
                "Published content not found."
            )

        serializer = ShareSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save(
            content=content,
            user=(
                request.user
                if request.user.is_authenticated
                else None
            ),
        )

        return Response({
            "message": "Share activity recorded.",
            "shares_count": content.shares.count(),
        }, status=status.HTTP_201_CREATED)


# ==========================================
# COMMENTS
# ==========================================

class CommentListCreateView(generics.ListCreateAPIView):

    serializer_class = CommentSerializer

    permission_classes = [IsAuthenticated]

    def get_content(self):

        content = get_published_content(
            self.kwargs["pk"]
        )

        if not content:
            raise NotFound(
                "Published content not found."
            )

        return content

    def get_queryset(self):

        content = self.get_content()

        return Comment.objects.filter(
            content=content,
            parent__isnull=True,
            is_hidden=False,
        ).select_related(
            "user",
            "content",
        ).prefetch_related(
            "replies__user"
        )

    def perform_create(self, serializer):

        content = self.get_content()

        serializer.save(
            content=content,
            user=self.request.user,
        )


# ==========================================
# COMMENT REPLIES
# ==========================================

class CommentReplyListView(generics.ListAPIView):

    serializer_class = CommentSerializer

    permission_classes = [AllowAny]

    def get_queryset(self):

        parent = Comment.objects.filter(
            pk=self.kwargs["comment_id"],
            parent__isnull=True,
            is_hidden=False,
            content__status=ContentItem.Status.PUBLISHED,
            content__published_at__lte=timezone.now(),
        ).first()

        if not parent:
            raise NotFound(
                "Comment not found."
            )

        return Comment.objects.filter(
            parent=parent,
            is_hidden=False,
        ).select_related(
            "user",
            "content",
        )


# ==========================================
# COMMENT DETAIL, UPDATE AND DELETE
# ==========================================

class CommentDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = CommentSerializer

    permission_classes = [IsAuthenticated]

    lookup_field = "id"

    def get_queryset(self):

        return Comment.objects.filter(
            is_hidden=False,
            content__status=ContentItem.Status.PUBLISHED,
            content__published_at__lte=timezone.now(),
        ).select_related(
            "user",
            "content",
        )

    def get_object(self):

        comment = super().get_object()

        is_owner = (
            comment.user_id == self.request.user.id
        )

        moderator = is_moderator(
            self.request.user
        )

        if not is_owner and not moderator:

            raise PermissionDenied(
                "You cannot manage this comment."
            )

        return comment

    def perform_update(self, serializer):

        serializer.save(
            edited_at=timezone.now()
        )


# ==========================================
# COMMENT MODERATION
# ==========================================

class CommentModerationView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id):

        if not is_moderator(request.user):

            raise PermissionDenied(
                "You are not authorized to moderate comments."
            )

        comment = Comment.objects.filter(
            pk=comment_id,
            content__status=ContentItem.Status.PUBLISHED,
        ).first()

        if not comment:

            raise NotFound(
                "Comment not found."
            )

        action = request.data.get("action")

        reason = request.data.get(
            "reason",
            ""
        )

        if action == "hide":

            comment.is_hidden = True
            comment.hidden_reason = reason

        elif action == "restore":

            comment.is_hidden = False
            comment.hidden_reason = ""

        else:

            raise ValidationError({
                "action": "Invalid moderation action."
            })

        comment.save(
            update_fields=[
                "is_hidden",
                "hidden_reason",
                "updated_at",
            ]
        )

        return Response({
            "message": "Comment moderation completed.",
            "is_hidden": comment.is_hidden,
        })


# ==========================================
# CREATE REPORT
# ==========================================

class CreateReportView(generics.CreateAPIView):

    serializer_class = ReportSerializer

    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):

        serializer.save(
            reporter=self.request.user
        )


# ==========================================
# MY REPORTS
# ==========================================

class MyReportsView(generics.ListAPIView):

    serializer_class = ReportSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return Report.objects.filter(
            reporter=self.request.user
        ).select_related(
            "content",
            "comment",
        )


# ==========================================
# REPORT MANAGEMENT
# ==========================================

class ReportManagementView(generics.ListAPIView):

    serializer_class = ReportSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        if not is_moderator(self.request.user):

            raise PermissionDenied(
                "You are not authorized to manage reports."
            )

        return Report.objects.select_related(
            "reporter",
            "content",
            "comment",
            "reviewed_by",
        )


# ==========================================
# RESOLVE REPORT
# ==========================================

class ResolveReportView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, report_id):

        if not is_moderator(request.user):

            raise PermissionDenied(
                "You cannot manage reports."
            )

        report = Report.objects.filter(
            pk=report_id
        ).first()

        if not report:

            raise NotFound(
                "Report not found."
            )

        action = request.data.get("action")

        notes = request.data.get(
            "notes",
            ""
        )

        if action == "resolve":

            report.status = Report.Status.RESOLVED

        elif action == "dismiss":

            report.status = Report.Status.DISMISSED

        elif action == "review":

            report.status = Report.Status.REVIEWING

        else:

            raise ValidationError({
                "action": "Invalid report action."
            })

        report.reviewed_by = request.user

        report.moderator_notes = notes

        report.reviewed_at = timezone.now()

        report.save(
            update_fields=[
                "status",
                "reviewed_by",
                "moderator_notes",
                "reviewed_at",
            ]
        )

        return Response({
            "message": "Report updated successfully.",
            "status": report.status,
        })


# ==========================================
# CONTENT ENGAGEMENT SUMMARY
# ==========================================

class ContentEngagementSummaryView(APIView):

    permission_classes = [AllowAny]

    def get(self, request, pk):

        content = get_published_content(pk)

        if not content:

            raise NotFound(
                "Published content not found."
            )

        user = request.user

        liked = False
        bookmarked = False

        if user.is_authenticated:

            liked = Like.objects.filter(
                user=user,
                content=content,
            ).exists()

            bookmarked = Bookmark.objects.filter(
                user=user,
                content=content,
            ).exists()

        return Response({

            "content_id": str(content.id),

            "likes_count": content.likes.count(),

            "comments_count": content.comments.filter(
                is_hidden=False
            ).count(),

            "shares_count": content.shares.count(),

            "bookmarks_count": content.bookmarks.count(),

            "liked": liked,

            "bookmarked": bookmarked,

        })