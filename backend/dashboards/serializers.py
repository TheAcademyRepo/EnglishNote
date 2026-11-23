from django.contrib.auth import get_user_model

from rest_framework import serializers

from app.roles import UserRole
from app.role_permissions import get_user_role

from publishing.models import ContentItem

User = get_user_model()


class DashboardUserSerializer(serializers.ModelSerializer):

    role = serializers.SerializerMethodField()

    class Meta:

        model = User

        fields = [
            "id",
            "username",
            "email",
            "is_active",
            "date_joined",
            "role",
        ]

    def get_role(self, obj):

        return get_user_role(obj)


class DashboardContentSerializer(serializers.ModelSerializer):

    author_username = serializers.CharField(
        source="author.username",
        read_only=True
    )

    class Meta:

        model = ContentItem

        fields = [
            "id",
            "content_type",
            "title",
            "slug",
            "excerpt",
            "author",
            "author_username",
            "status",
            "views",
            "created_at",
            "updated_at",
            "published_at",
        ]

        read_only_fields = fields