from django.conf import settings
from django.db import models


class Notification(models.Model):

    class NotificationType(models.TextChoices):
        LIKE = "like", "Like"
        COMMENT = "comment", "Comment"
        REPLY = "reply", "Reply"
        PUBLISHED = "published", "Published"
        REVIEW = "review", "Review"
        FOLLOW = "follow", "Follow"
        SYSTEM = "system", "System"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_notifications"
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_notifications"
    )

    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices
    )

    message = models.CharField(max_length=255)

    content = models.ForeignKey(
        "publishing.ContentItem",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )

    comment = models.ForeignKey(
        "engagement.Comment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["recipient", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.notification_type}: {self.message}"