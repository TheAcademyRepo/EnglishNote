from rest_framework import serializers

from publishing.models import ContentItem


class DiscoveryContentSerializer(serializers.ModelSerializer):

    author_username = serializers.CharField(
        source="author.username",
        read_only=True
    )

    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
        default=None
    )

    topic_name = serializers.CharField(
        source="topic.name",
        read_only=True,
        default=None
    )

    class Meta:
        model = ContentItem

        fields = [
            "id",
            "content_type",
            "title",
            "slug",
            "excerpt",
            "image",
            "author",
            "author_username",
            "category",
            "category_name",
            "topic",
            "topic_name",
            "status",
            "views",
            "published_at",
            "created_at",
        ]

        read_only_fields = fields