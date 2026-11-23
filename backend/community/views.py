from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from rest_framework import (
    generics,
    permissions,
    status,
)

from rest_framework.views import APIView
from rest_framework.response import Response

from publishing.models import ContentItem

from notifications.models import Notification

from .models import CommunityProfile, Follow
from .serializers import (
    CommunityProfileSerializer,
    UserSummarySerializer,
)

User = get_user_model()


class MyProfileView(generics.RetrieveUpdateAPIView):

    serializer_class = CommunityProfileSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_object(self):

        profile, created = CommunityProfile.objects.get_or_create(
            user=self.request.user
        )

        return profile


class PublicProfileView(generics.RetrieveAPIView):

    serializer_class = CommunityProfileSerializer

    permission_classes = [
        permissions.AllowAny
    ]

    lookup_field = "username"

    def get_object(self):

        user = get_object_or_404(
            User,
            username=self.kwargs["username"]
        )

        return get_object_or_404(
            CommunityProfile,
            user=user
        )


class FollowToggleView(APIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def post(self, request, username):

        target = get_object_or_404(
            User,
            username=username
        )

        if target.pk == request.user.pk:

            return Response(
                {"error": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():

            follow, created = Follow.objects.get_or_create(
                follower=request.user,
                following=target
            )

            if created:

                Notification.objects.create(
                    recipient=target,
                    actor=request.user,
                    notification_type=Notification.NotificationType.FOLLOW,
                    message=f"{request.user.username} started following you."
                )

                return Response({
                    "message": "You are now following this user.",
                    "is_following": True,
                })

            follow.delete()

            return Response({
                "message": "You unfollowed this user.",
                "is_following": False,
            })


class FollowersListView(generics.ListAPIView):

    serializer_class = UserSummarySerializer

    permission_classes = [
        permissions.AllowAny
    ]

    def get_queryset(self):

        user = get_object_or_404(
            User,
            username=self.kwargs["username"]
        )

        return User.objects.filter(
            following_relationships__following=user
        ).select_related(
            "community_profile"
        ).order_by(
            "-following_relationships__created_at"
        )


class FollowingListView(generics.ListAPIView):

    serializer_class = UserSummarySerializer

    permission_classes = [
        permissions.AllowAny
    ]

    def get_queryset(self):

        user = get_object_or_404(
            User,
            username=self.kwargs["username"]
        )

        return User.objects.filter(
            follower_relationships__follower=user
        ).select_related(
            "community_profile"
        ).order_by(
            "-follower_relationships__created_at"
        )


class AuthorContentView(generics.ListAPIView):

    permission_classes = [
        permissions.AllowAny
    ]

    def get_queryset(self):

        user = get_object_or_404(
            User,
            username=self.kwargs["username"]
        )

        return ContentItem.objects.filter(
            author=user,
            status=ContentItem.Status.PUBLISHED
        ).select_related(
            "author",
            "category",
            "topic"
        ).order_by(
            "-published_at"
        )

    def get_serializer_class(self):

        from discovery.serializers import DiscoveryContentSerializer

        return DiscoveryContentSerializer


class AuthorStatisticsView(APIView):

    permission_classes = [
        permissions.AllowAny
    ]

    def get(self, request, username):

        author = get_object_or_404(
            User,
            username=username
        )

        published = ContentItem.objects.filter(
            author=author,
            status=ContentItem.Status.PUBLISHED
        )

        followers = Follow.objects.filter(
            following=author
        ).count()

        following = Follow.objects.filter(
            follower=author
        ).count()

        return Response({

            "username": author.username,

            "followers": followers,

            "following": following,

            "published_content": published.count(),

            "total_views": sum(
                published.values_list("views", flat=True)
            ),

            "content_by_type": {
                "blogs": published.filter(
                    content_type="blog"
                ).count(),

                "posts": published.filter(
                    content_type="post"
                ).count(),

                "daily_posts": published.filter(
                    content_type="daily"
                ).count(),
            },

        })


class SuggestedAuthorsView(generics.ListAPIView):

    serializer_class = UserSummarySerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):

        user = self.request.user

        already_following = Follow.objects.filter(
            follower=user
        ).values_list(
            "following_id",
            flat=True
        )

        return User.objects.filter(
            content_items__status=ContentItem.Status.PUBLISHED
        ).exclude(
            id=user.id
        ).exclude(
            id__in=already_following
        ).annotate(
            published_count=Count(
                "content_items",
                filter=Q(
                    content_items__status=ContentItem.Status.PUBLISHED
                ),
                distinct=True
            )
        ).order_by(
            "-published_count"
        ).distinct()


class PersonalizedFeedView(generics.ListAPIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_serializer_class(self):

        from discovery.serializers import DiscoveryContentSerializer

        return DiscoveryContentSerializer

    def get_queryset(self):

        user = self.request.user

        followed_users = Follow.objects.filter(
            follower=user
        ).values_list(
            "following_id",
            flat=True
        )

        return ContentItem.objects.filter(
            Q(author=user) | Q(author_id__in=followed_users),
            status=ContentItem.Status.PUBLISHED
        ).select_related(
            "author",
            "category",
            "topic"
        ).order_by(
            "-published_at"
        ).distinct()