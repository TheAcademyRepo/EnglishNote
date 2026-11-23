from rest_framework import serializers

from .models import (
    Like,
    Bookmark,
    Share,
    Comment,
    Report,
)


class LikeSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    class Meta:
        model = Like

        fields = [
            "id",
            "username",
            "created_at",
        ]


class BookmarkSerializer(serializers.ModelSerializer):

    content_title = serializers.CharField(
        source="content.title",
        read_only=True,
    )

    content_slug = serializers.CharField(
        source="content.slug",
        read_only=True,
    )

    class Meta:
        model = Bookmark

        fields = [
            "id",
            "content",
            "content_title",
            "content_slug",
            "created_at",
        ]


class ShareSerializer(serializers.ModelSerializer):

    class Meta:
        model = Share

        fields = [
            "id",
            "content",
            "platform",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "content",
            "created_at",
        ]


class CommentSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment

        fields = [
            "id",
            "content",
            "user",
            "username",
            "parent",
            "body",
            "is_hidden",
            "replies_count",
            "edited_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "content",
            "user",
            "username",
            "is_hidden",
            "edited_at",
            "created_at",
            "updated_at",
        ]

    def get_replies_count(self, obj):

        return obj.replies.filter(
            is_hidden=False
        ).count()

    def validate_body(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "A comment cannot be empty."
            )

        return value

    def validate_parent(self, parent):

        if parent:

            if parent.parent_id is not None:
                raise serializers.ValidationError(
                    "Replies to replies are not supported."
                )

            if parent.is_hidden:
                raise serializers.ValidationError(
                    "You cannot reply to a hidden comment."
                )

            if parent.content.status != "published":
                raise serializers.ValidationError(
                    "You cannot reply to this comment."
                )

        return parent

    def validate(self, attrs):

        parent = attrs.get(
            "parent",
            getattr(self.instance, "parent", None),
        )

        content = attrs.get(
            "content",
            getattr(self.instance, "content", None),
        )

        if parent and content and parent.content_id != content.id:
            raise serializers.ValidationError({
                "parent": "A reply must belong to the same content as its parent."
            })

        return attrs


class ReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Report

        fields = [
            "id",
            "target_type",
            "content",
            "comment",
            "reason",
            "description",
            "status",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "created_at",
        ]

    def validate(self, attrs):

        target_type = attrs.get("target_type")

        content = attrs.get("content")
        comment = attrs.get("comment")

        request = self.context.get("request")

        if target_type == Report.TargetType.CONTENT:

            if not content or comment:
                raise serializers.ValidationError(
                    "Select exactly one content item to report."
                )

            if content.status != "published":
                raise serializers.ValidationError(
                    "Only published content can be reported."
                )

            if request and content.author_id == request.user.id:
                raise serializers.ValidationError(
                    "You cannot report your own content."
                )

        elif target_type == Report.TargetType.COMMENT:

            if not comment or content:
                raise serializers.ValidationError(
                    "Select exactly one comment to report."
                )

            if request and comment.user_id == request.user.id:
                raise serializers.ValidationError(
                    "You cannot report your own comment."
                )

        else:

            raise serializers.ValidationError(
                "Invalid report target."
            )

        return attrs