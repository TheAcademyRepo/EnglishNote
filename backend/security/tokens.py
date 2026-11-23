import hashlib
import secrets

from datetime import timedelta

from django.utils import timezone

from .models import SecurityToken


def generate_secure_token():

    return secrets.token_urlsafe(48)


def hash_token(token):

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def create_security_token(user, token_type, lifetime_minutes):

    SecurityToken.objects.filter(
        user=user,
        token_type=token_type,
        used_at__isnull=True
    ).update(
        used_at=timezone.now()
    )

    raw_token = generate_secure_token()

    SecurityToken.objects.create(
        user=user,
        token_hash=hash_token(raw_token),
        token_type=token_type,
        expires_at=timezone.now() + timedelta(
            minutes=lifetime_minutes
        )
    )

    return raw_token