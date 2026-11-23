from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import CommunityProfile, Follow

User = get_user_model()


class CommunityProfileSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    display_name = serializers.CharField(
        required=False,
        allow_blank=True
    )

    followers_count = serializers.SerializerMethodField()

    following_count = serializers.SerializerMethodField()

    class Meta:

        model = CommunityProfile

        fields = [
            "id",
            "username",
            "display_name",
            "bio",
            "avatar",
            "cover_image",
            "website",
            "location",
            "occupation",
            "followers_count",
            "following_count",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "username",
            "followers_count",
            "following_count",
            "created_at",
            "updated_at",
        ]

    def get_followers_count(self, obj):

        return Follow.objects.filter(
            following=obj.user
        ).count()

    def get_following_count(self, obj):

        return Follow.objects.filter(
            follower=obj.user
        ).count()


class UserSummarySerializer(serializers.ModelSerializer):

    display_name = serializers.SerializerMethodField()

    avatar = serializers.SerializerMethodField()

    followers_count = serializers.SerializerMethodField()

    is_following = serializers.SerializerMethodField()

    class Meta:

        model = User

        fields = [
            "id",
            "username",
            "display_name",
            "avatar",
            "followers_count",
            "is_following",
        ]

    def get_display_name(self, obj):

        profile = getattr(obj, "community_profile", None)

        if profile and profile.display_name:
            return profile.display_name

        return obj.username

    def get_avatar(self, obj):

        profile = getattr(obj, "community_profile", None)

        if profile and profile.avatar:
            request = self.context.get("request")

            if request:
                return request.build_absolute_uri(profile.avatar.url)

            return profile.avatar.url

        return None

    def get_followers_count(self, obj):

        return Follow.objects.filter(
            following=obj
        ).count()

    def get_is_following(self, obj):

        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return False

        return Follow.objects.filter(
            follower=request.user,
            following=obj
        ).exists()