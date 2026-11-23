from rest_framework import serializers

from .models import ContentItem, ContentReview, ContentVersion


class ContentItemSerializer(serializers.ModelSerializer):

    author_username = serializers.CharField(
        source="author.username",
        read_only=True
    )

    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    topic_name = serializers.CharField(
        source="topic.name",
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
            "body",
            "image",
            "author",
            "author_username",
            "category",
            "category_name",
            "topic",
            "topic_name",
            "status",
            "review_notes",
            "rejection_reason",
            "scheduled_at",
            "published_at",
            "views",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "slug",
            "author",
            "status",
            "review_notes",
            "rejection_reason",
            "published_at",
            "views",
            "created_at",
            "updated_at",
        ]

    def validate_content_type(self, value):

        request = self.context.get("request")

        if not request:
            return value

        from app.role_permissions import get_user_role

        role = get_user_role(request.user)

        if value == ContentItem.ContentType.DAILY:

            if role not in [
                "author",
                "administrator",
                "super_administrator",
            ]:

                raise serializers.ValidationError(
                    "You are not permitted to create daily posts."
                )

        if value in [
            ContentItem.ContentType.BLOG,
            ContentItem.ContentType.POST,
        ]:

            if role not in [
                "contributor",
                "author",
                "administrator",
                "super_administrator",
            ]:

                raise serializers.ValidationError(
                    "You are not permitted to create this content."
                )

        return value


class ContentReviewSerializer(serializers.ModelSerializer):

    reviewer_username = serializers.CharField(
        source="reviewer.username",
        read_only=True
    )

    class Meta:

        model = ContentReview

        fields = [
            "id",
            "content",
            "reviewer",
            "reviewer_username",
            "decision",
            "feedback",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "reviewer",
            "created_at",
        ]


class ContentVersionSerializer(serializers.ModelSerializer):

    editor_username = serializers.CharField(
        source="edited_by.username",
        read_only=True
    )

    class Meta:

        model = ContentVersion

        fields = [
            "id",
            "title",
            "body",
            "editor_username",
            "created_at",
        ]