import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from publishing.models import ContentItem


class Like(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="content_likes"
    )

    content = models.ForeignKey(
        ContentItem,
        on_delete=models.CASCADE,
        related_name="likes"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=["user", "content"],
                name="unique_user_content_like"
            )
        ]

        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} liked {self.content}"


class Bookmark(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="content_bookmarks"
    )

    content = models.ForeignKey(
        ContentItem,
        on_delete=models.CASCADE,
        related_name="bookmarks"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=["user", "content"],
                name="unique_user_content_bookmark"
            )
        ]

        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} bookmarked {self.content}"


class Share(models.Model):

    class Platform(models.TextChoices):
        WHATSAPP = "whatsapp", "WhatsApp"
        FACEBOOK = "facebook", "Facebook"
        X = "x", "X"
        TELEGRAM = "telegram", "Telegram"
        LINK = "link", "Copied Link"
        OTHER = "other", "Other"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="content_shares"
    )

    content = models.ForeignKey(
        ContentItem,
        on_delete=models.CASCADE,
        related_name="shares"
    )

    platform = models.CharField(
        max_length=20,
        choices=Platform.choices,
        default=Platform.LINK
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.content.title} - {self.platform}"


class Comment(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    content = models.ForeignKey(
        ContentItem,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="engagement_comments"
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )

    body = models.TextField(
        max_length=5000
    )

    is_hidden = models.BooleanField(
        default=False
    )

    hidden_reason = models.TextField(
        blank=True
    )

    edited_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ["created_at"]

        indexes = [
            models.Index(fields=["content", "created_at"]),
            models.Index(fields=["parent", "created_at"]),
        ]

    def __str__(self):
        return f"Comment by {self.user} on {self.content}"


class Report(models.Model):

    class TargetType(models.TextChoices):
        CONTENT = "content", "Content"
        COMMENT = "comment", "Comment"

    class Reason(models.TextChoices):
        SPAM = "spam", "Spam"
        HARASSMENT = "harassment", "Harassment"
        HATE = "hate", "Hate Speech"
        MISINFORMATION = "misinformation", "Misinformation"
        COPYRIGHT = "copyright", "Copyright Violation"
        INAPPROPRIATE = "inappropriate", "Inappropriate Content"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        REVIEWING = "reviewing", "Under Review"
        RESOLVED = "resolved", "Resolved"
        DISMISSED = "dismissed", "Dismissed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submitted_reports"
    )

    target_type = models.CharField(
        max_length=20,
        choices=TargetType.choices
    )

    content = models.ForeignKey(
        ContentItem,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reports"
    )

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reports"
    )

    reason = models.CharField(
        max_length=30,
        choices=Reason.choices
    )

    description = models.TextField(
        max_length=2000,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_reports"
    )

    moderator_notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:

        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["status", "created_at"]),
        ]

    def clean(self):

        from django.core.exceptions import ValidationError

        if self.target_type == self.TargetType.CONTENT:

            if not self.content_id or self.comment_id:
                raise ValidationError(
                    "A content report must reference exactly one content item."
                )

        elif self.target_type == self.TargetType.COMMENT:

            if not self.comment_id or self.content_id:
                raise ValidationError(
                    "A comment report must reference exactly one comment."
                )

        if self.comment_id and self.comment.content_id:
            if self.content_id:
                raise ValidationError(
                    "A report cannot reference both content and a comment."
                )

    def save(self, *args, **kwargs):

        if self.target_type == self.TargetType.COMMENT and self.comment_id:
            self.content_id = None

        if self.target_type == self.TargetType.CONTENT and self.content_id:
            self.comment_id = None

        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reporter} - {self.reason}"