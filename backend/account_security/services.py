from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator


def get_frontend_url(path, user, token):

    base_url = getattr(
        settings,
        "FRONTEND_URL",
        "http://localhost:5173"
    ).rstrip("/")

    return (
        f"{base_url}{path}"
        f"?user_id={user.id}&token={token}"
    )


def send_verification_email(user):

    token = default_token_generator.make_token(user)

    link = get_frontend_url(
        "/verify-email/",
        user,
        token
    )

    send_mail(
        subject="Verify your EnglishNote account",

        message=(
            f"Hello {user.username},\n\n"
            f"Please verify your email address:\n\n"
            f"{link}\n\n"
            f"If you did not create this account, "
            f"you can ignore this email."
        ),

        from_email=None,

        recipient_list=[user.email],

        fail_silently=False
    )


def send_password_reset_email(user):

    token = default_token_generator.make_token(user)

    link = get_frontend_url(
        "/reset-password/",
        user,
        token
    )

    send_mail(
        subject="Reset your EnglishNote password",

        message=(
            f"Hello {user.username},\n\n"
            f"Use the link below to reset your password:\n\n"
            f"{link}\n\n"
            f"If you did not request this, ignore this email."
        ),

        from_email=None,

        recipient_list=[user.email],

        fail_silently=False
    )