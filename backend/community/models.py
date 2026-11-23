from django.conf import settings
from django.db import models
from django.core.validators import URLValidator


class CommunityProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="community_profile"
    )

    display_name = models.CharField(
        max_length=100,
        blank=True
    )

    bio = models.TextField(
        max_length=500,
        blank=True
    )

    avatar = models.ImageField(
        upload_to="community/avatars/",
        blank=True,
        null=True
    )

    cover_image = models.ImageField(
        upload_to="community/covers/",
        blank=True,
        null=True
    )

    website = models.URLField(
        blank=True
    )

    location = models.CharField(
        max_length=100,
        blank=True
    )

    occupation = models.CharField(
        max_length=100,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.display_name or self.user.username


class Follow(models.Model):

    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following_relationships"
    )

    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="follower_relationships"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"],
                name="unique_user_follow"
            ),

            models.CheckConstraint(
                condition=~models.Q(follower=models.F("following")),
                name="prevent_self_follow"
            ),
        ]

        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["follower", "-created_at"]),
            models.Index(fields=["following", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.follower} follows {self.following}"