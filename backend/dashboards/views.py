from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, generics

from app.roles import UserRole
from app.role_permissions import get_user_role

from app.models import (
    Subject,
    Topic,
    Note,
    Category,
)

from publishing.models import ContentItem

from engagement.models import (
    Like,
    Bookmark,
    Comment,
    Report,
    Share,
)

from community.models import Follow
from notifications.models import Notification

from .serializers import (
    DashboardUserSerializer,
    DashboardContentSerializer,
)

User = get_user_model()


# =========================================
# DASHBOARD OVERVIEW
# =========================================

class DashboardOverviewView(APIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request):

        user = request.user
        role = get_user_role(user)

        data = {
            "username": user.username,
            "role": role,
        }

        # =====================================
        # STUDENT DASHBOARD
        # =====================================

        if role == UserRole.STUDENT:

            data["statistics"] = {

                "bookmarks": Bookmark.objects.filter(
                    user=user
                ).count(),

                "comments": Comment.objects.filter(
                    user=user
                ).count(),

                "following": Follow.objects.filter(
                    follower=user
                ).count(),

                "followers": Follow.objects.filter(
                    following=user
                ).count(),

                "notifications": Notification.objects.filter(
                    recipient=user,
                    is_read=False
                ).count(),

            }

        # =====================================
        # CONTRIBUTOR DASHBOARD
        # =====================================

        elif role == UserRole.CONTRIBUTOR:

            content = ContentItem.objects.filter(
                author=user
            )

            data["statistics"] = {

                "total_content": content.count(),

                "drafts": content.filter(
                    status=ContentItem.Status.DRAFT
                ).count(),

                "submitted": content.filter(
                    status=ContentItem.Status.SUBMITTED
                ).count(),

                "in_review": content.filter(
                    status=ContentItem.Status.IN_REVIEW
                ).count(),

                "approved": content.filter(
                    status=ContentItem.Status.APPROVED
                ).count(),

                "rejected": content.filter(
                    status=ContentItem.Status.REJECTED
                ).count(),

                "published": content.filter(
                    status=ContentItem.Status.PUBLISHED
                ).count(),

            }

        # =====================================
        # AUTHOR DASHBOARD
        # =====================================

        elif role == UserRole.AUTHOR:

            content = ContentItem.objects.filter(
                author=user
            )

            data["statistics"] = {

                "total_content": content.count(),

                "published": content.filter(
                    status=ContentItem.Status.PUBLISHED
                ).count(),

                "drafts": content.filter(
                    status=ContentItem.Status.DRAFT
                ).count(),

                "submitted": content.filter(
                    status=ContentItem.Status.SUBMITTED
                ).count(),

                "rejected": content.filter(
                    status=ContentItem.Status.REJECTED
                ).count(),

                "total_views": sum(
                    content.values_list(
                        "views",
                        flat=True
                    )
                ),

                "followers": Follow.objects.filter(
                    following=user
                ).count(),

                "following": Follow.objects.filter(
                    follower=user
                ).count(),

                "comments_on_content": Comment.objects.filter(
                    content__author=user
                ).count(),

                "likes_on_content": Like.objects.filter(
                    content__author=user
                ).count(),

                "unresolved_reports": Report.objects.filter(
                    status="pending",
                    content__author=user
                ).count(),

            }

        # =====================================
        # EDITOR DASHBOARD
        # =====================================

        elif role == UserRole.EDITOR:

            data["statistics"] = {

                "subjects": Subject.objects.count(),

                "topics": Topic.objects.count(),

                "lessons": Note.objects.count(),

                "submitted_content": ContentItem.objects.filter(
                    status=ContentItem.Status.SUBMITTED
                ).count(),

                "content_in_review": ContentItem.objects.filter(
                    status=ContentItem.Status.IN_REVIEW
                ).count(),

                "comments": Comment.objects.count(),

                "pending_reports": Report.objects.filter(
                    status="pending"
                ).count(),

            }

        # =====================================
        # ADMINISTRATOR DASHBOARD
        # =====================================

        elif role in [
            UserRole.ADMINISTRATOR,
            UserRole.SUPER_ADMINISTRATOR,
        ]:

            content = ContentItem.objects.all()

            data["statistics"] = {

                "total_users": User.objects.count(),

                "active_users": User.objects.filter(
                    is_active=True
                ).count(),

                "total_subjects": Subject.objects.count(),

                "total_topics": Topic.objects.count(),

                "total_lessons": Note.objects.count(),

                "total_categories": Category.objects.count(),

                "total_content": content.count(),

                "published_content": content.filter(
                    status=ContentItem.Status.PUBLISHED
                ).count(),

                "pending_content": content.filter(
                    status__in=[
                        ContentItem.Status.SUBMITTED,
                        ContentItem.Status.IN_REVIEW,
                    ]
                ).count(),

                "pending_reports": Report.objects.filter(
                    status="pending"
                ).count(),

                "total_comments": Comment.objects.count(),

                "total_likes": Like.objects.count(),

            }

        else:

            return Response(
                {
                    "error": "No dashboard is configured for this role."
                },
                status=403
            )

        return Response(data)


# =========================================
# MY CONTENT MANAGEMENT
# =========================================

class MyDashboardContentView(generics.ListAPIView):

    serializer_class = DashboardContentSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):

        role = get_user_role(self.request.user)

        allowed_roles = [
            UserRole.CONTRIBUTOR,
            UserRole.AUTHOR,
            UserRole.ADMINISTRATOR,
            UserRole.SUPER_ADMINISTRATOR,
        ]

        if role not in allowed_roles:
            return ContentItem.objects.none()

        return ContentItem.objects.filter(
            author=self.request.user
        ).order_by("-created_at")


# =========================================
# CONTENT REVIEW QUEUE
# =========================================

class ContentReviewQueueView(generics.ListAPIView):

    serializer_class = DashboardContentSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):

        role = get_user_role(self.request.user)

        allowed_roles = [
            UserRole.AUTHOR,
            UserRole.EDITOR,
            UserRole.ADMINISTRATOR,
            UserRole.SUPER_ADMINISTRATOR,
        ]

        if role not in allowed_roles:
            return ContentItem.objects.none()

        return ContentItem.objects.filter(
            status__in=[
                ContentItem.Status.SUBMITTED,
                ContentItem.Status.IN_REVIEW,
            ]
        ).select_related(
            "author"
        ).order_by("created_at")


# =========================================
# ADMIN USER MANAGEMENT
# =========================================

class DashboardUserListView(generics.ListAPIView):

    serializer_class = DashboardUserSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):

        role = get_user_role(self.request.user)

        if role not in [
            UserRole.ADMINISTRATOR,
            UserRole.SUPER_ADMINISTRATOR,
        ]:

            return User.objects.none()

        queryset = User.objects.all().order_by(
            "-date_joined"
        )

        search = self.request.query_params.get("q")

        if search:

            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
            )

        return queryset.distinct()


# =========================================
# ADMIN PLATFORM STATISTICS
# =========================================

class PlatformStatisticsView(APIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request):

        role = get_user_role(request.user)

        if role not in [
            UserRole.ADMINISTRATOR,
            UserRole.SUPER_ADMINISTRATOR,
        ]:

            return Response(
                {
                    "error": "You do not have permission."
                },
                status=403
            )

        content = ContentItem.objects.all()

        return Response({

            "users": {

                "total": User.objects.count(),

                "active": User.objects.filter(
                    is_active=True
                ).count(),

                "inactive": User.objects.filter(
                    is_active=False
                ).count(),

            },

            "content": {

                "total": content.count(),

                "published": content.filter(
                    status=ContentItem.Status.PUBLISHED
                ).count(),

                "drafts": content.filter(
                    status=ContentItem.Status.DRAFT
                ).count(),

                "pending": content.filter(
                    status__in=[
                        ContentItem.Status.SUBMITTED,
                        ContentItem.Status.IN_REVIEW,
                    ]
                ).count(),

                "rejected": content.filter(
                    status=ContentItem.Status.REJECTED
                ).count(),

            },

            "engagement": {

                "likes": Like.objects.count(),

                "comments": Comment.objects.count(),

                "bookmarks": Bookmark.objects.count(),

                "shares": Share.objects.count(),

            },

            "learning": {

                "subjects": Subject.objects.count(),

                "topics": Topic.objects.count(),

                "lessons": Note.objects.count(),

            },

        })