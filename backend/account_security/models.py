import uuid
import hashlib
import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class RoleInvitation(models.Model):

    class Status(models.TextChoices):

        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        EXPIRED = "expired", "Expired"
        REVOKED = "revoked", "Revoked"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    email = models.EmailField()

    role = models.CharField(
        max_length=30,
        choices=[
            ("contributor", "Contributor"),
            ("author", "Author"),
            ("editor", "Editor"),
            ("administrator", "Administrator"),
        ]
    )

    token_hash = models.CharField(
        max_length=64,
        unique=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_role_invitations"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    expires_at = models.DateTimeField()

    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accepted_role_invitations"
    )

    accepted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    @staticmethod
    def hash_token(token):

        return hashlib.sha256(
            token.encode()
        ).hexdigest()

    @staticmethod
    def generate_token():

        return secrets.token_urlsafe(48)

    def is_expired(self):

        return timezone.now() >= self.expires_at

    def clean(self):

        if self.created_by_id and not (
            self.created_by.is_superuser
            or getattr(
                getattr(self.created_by, "role_assignment", None),
                "role",
                None
            ) in ["administrator", "super_administrator"]
        ):

            raise ValidationError(
                "Only authorized administrators can issue invitations."
            )

    def __str__(self):

        return f"{self.email} - {self.role}"