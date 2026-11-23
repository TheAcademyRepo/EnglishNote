from django.conf import settings
from django.db import models


class UserProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    display_name = models.CharField(
        max_length=100,
        blank=True
    )

    bio = models.TextField(
        max_length=1000,
        blank=True
    )

    avatar_url = models.URLField(
        blank=True
    )

    website = models.URLField(
        blank=True
    )

    location = models.CharField(
        max_length=150,
        blank=True
    )

    is_private = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.display_name or self.user.username


class RoleAssignment(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="role_assignment"
    )

    role = models.CharField(
        max_length=30,
        choices=[
            ("student", "Student"),
            ("contributor", "Contributor"),
            ("author", "Author"),
            ("editor", "Editor"),
            ("administrator", "Administrator"),
            ("super_administrator", "Super Administrator"),
        ],
        default="student"
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_roles"
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"