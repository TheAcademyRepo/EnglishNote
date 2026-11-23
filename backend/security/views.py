from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from app.role_models import RoleAssignment, UserProfile
from app.roles import UserRole
from app.role_permissions import is_authorized_administrator

from .models import SecurityToken, StaffInvitation
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
)

from .tokens import (
    generate_secure_token,
    hash_token,
    create_security_token,
)

User = get_user_model()


def send_security_email(subject, message, email):

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )


def issue_verification_email(user):

    token = create_security_token(
        user,
        SecurityToken.TokenType.EMAIL_VERIFICATION,
        30
    )

    link = (
        f"{settings.FRONTEND_URL}/verify-email"
        f"?token={token}"
    )

    send_security_email(
        "Verify your EnglishNote account",
        (
            f"Hello {user.username},\n\n"
            "Welcome to EnglishNote.\n"
            "Please verify your email address using this link:\n\n"
            f"{link}\n\n"
            "This link expires in 30 minutes."
        ),
        user.email
    )


def get_user_role(user):

    if user.is_superuser:
        return UserRole.SUPER_ADMINISTRATOR

    try:
        return user.role_assignment.role
    except RoleAssignment.DoesNotExist:
        return UserRole.STUDENT


class RegisterView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = RegisterSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        try:
            issue_verification_email(user)

        except Exception:
            user.delete()

            return Response(
                {
                    "message": (
                        "Your account could not be completed because "
                        "the verification email could not be sent. "
                        "Please try again."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        return Response(
            {
                "message": (
                    "Your account has been created. "
                    "Please check your email to verify your account."
                )
            },
            status=status.HTTP_201_CREATED
        )


class VerifyEmailView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        raw_token = request.data.get("token")

        if not raw_token:
            return Response(
                {"message": "A verification token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        token = SecurityToken.objects.filter(
            token_hash=hash_token(raw_token),
            token_type=SecurityToken.TokenType.EMAIL_VERIFICATION,
            used_at__isnull=True
        ).select_related("user").first()

        if not token or not token.is_valid():

            return Response(
                {
                    "message": (
                        "This verification link is invalid or has expired. "
                        "Please request a new one."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():

            token.used_at = timezone.now()
            token.save(update_fields=["used_at"])

            user = token.user
            user.email_verified = True
            user.save(update_fields=["email_verified"])

        return Response({
            "message": "Your email address has been verified successfully."
        })


class ResendVerificationView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        email = request.data.get("email", "").strip().lower()

        user = User.objects.filter(
            email__iexact=email
        ).first()

        if user and not user.email_verified:

            try:
                issue_verification_email(user)

            except Exception:
                return Response(
                    {
                        "message": (
                            "We could not send the verification email. "
                            "Please try again later."
                        )
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

        return Response({
            "message": (
                "If an unverified account exists with that email, "
                "a verification link has been sent."
            )
        })


class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = LoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].lower()
        password = serializer.validated_data["password"]

        user_record = User.objects.filter(
            email__iexact=email
        ).first()

        if not user_record:

            return Response(
                {"message": "The email or password you entered is incorrect."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = authenticate(
            request,
            username=user_record.get_username(),
            password=password
        )

        if not user:

            return Response(
                {"message": "The email or password you entered is incorrect."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:

            return Response(
                {
                    "message": (
                        "Your account is currently inactive. "
                        "Please contact support."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if not user.email_verified:

            return Response(
                {
                    "message": (
                        "Please verify your email address before signing in."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "You have signed in successfully.",

            "access": str(refresh.access_token),

            "refresh": str(refresh),

            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": get_user_role(user),
            }
        })


class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        refresh_token = request.data.get("refresh")

        if not refresh_token:

            return Response(
                {"message": "A refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            token = RefreshToken(refresh_token)

            if token["user_id"] != request.user.id:

                return Response(
                    {"message": "Invalid refresh token."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token.blacklist()

        except Exception:

            return Response(
                {"message": "The refresh token is invalid or expired."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            "message": "You have signed out successfully."
        })


class MeView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            profile, _ = UserProfile.objects.get_or_create(
                user=user
            )

        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "email_verified": user.email_verified,
            "role": get_user_role(user),

            "profile": {
                "display_name": profile.display_name,
                "bio": profile.bio,
                "avatar_url": profile.avatar_url,
                "website": profile.website,
                "location": profile.location,
                "is_private": profile.is_private,
            }
        })


class ForgotPasswordView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = ForgotPasswordSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].lower()

        user = User.objects.filter(
            email__iexact=email,
            is_active=True
        ).first()

        if user:

            try:

                token = create_security_token(
                    user,
                    SecurityToken.TokenType.PASSWORD_RESET,
                    15
                )

                link = (
                    f"{settings.FRONTEND_URL}/reset-password"
                    f"?token={token}"
                )

                send_security_email(
                    "Reset your EnglishNote password",
                    (
                        "We received a request to reset your password.\n\n"
                        f"Use this link:\n{link}\n\n"
                        "This link expires in 15 minutes.\n"
                        "If you did not request this, ignore this email."
                    ),
                    user.email
                )

            except Exception:

                return Response(
                    {
                        "message": (
                            "We could not process your request. "
                            "Please try again later."
                        )
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

        return Response({
            "message": (
                "If an account exists with that email address, "
                "password reset instructions will be sent."
            )
        })


class ResetPasswordView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = ResetPasswordSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        raw_token = serializer.validated_data["token"]

        token = SecurityToken.objects.filter(
            token_hash=hash_token(raw_token),
            token_type=SecurityToken.TokenType.PASSWORD_RESET,
            used_at__isnull=True
        ).select_related("user").first()

        if not token or not token.is_valid():

            return Response(
                {"message": "This password reset link is invalid or expired."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = token.user

        with transaction.atomic():

            user.set_password(
                serializer.validated_data["password"]
            )

            user.save(update_fields=["password"])

            token.used_at = timezone.now()
            token.save(update_fields=["used_at"])

            SecurityToken.objects.filter(
                user=user,
                token_type=SecurityToken.TokenType.PASSWORD_RESET,
                used_at__isnull=True
            ).exclude(pk=token.pk).update(
                used_at=timezone.now()
            )

        return Response({
            "message": (
                "Your password has been reset successfully. "
                "Please sign in with your new password."
            )
        })


class ChangePasswordView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = ChangePasswordSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        user = request.user

        if not user.check_password(
            serializer.validated_data["current_password"]
        ):

            return Response(
                {"message": "Your current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(
            serializer.validated_data["new_password"]
        )

        user.save(update_fields=["password"])

        return Response({
            "message": "Your password has been changed successfully."
        })


class CreateInvitationView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        if not is_authorized_administrator(request.user):

            return Response(
                {"message": "You do not have permission to invite staff."},
                status=status.HTTP_403_FORBIDDEN
            )

        email = request.data.get("email", "").strip().lower()

        role = request.data.get("role", "").strip()

        if role not in [
            UserRole.CONTRIBUTOR,
            UserRole.AUTHOR,
            UserRole.EDITOR,
            UserRole.ADMINISTRATOR,
        ]:

            return Response(
                {"message": "The selected invitation role is not permitted."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if role == UserRole.ADMINISTRATOR and (
            get_user_role(request.user) != UserRole.SUPER_ADMINISTRATOR
        ):

            return Response(
                {"message": "Only a Super Administrator can invite Administrators."},
                status=status.HTTP_403_FORBIDDEN
            )

        if not email:

            return Response(
                {"message": "An email address is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email__iexact=email).exists():

            return Response(
                {"message": "An account already exists with this email address."},
                status=status.HTTP_400_BAD_REQUEST
            )

        raw_token = generate_secure_token()

        invitation = StaffInvitation.objects.create(
            email=email,
            role=role,
            token_hash=hash_token(raw_token),
            invited_by=request.user,
            expires_at=timezone.now() + timedelta(days=2)
        )

        link = (
            f"{settings.FRONTEND_URL}/accept-invitation"
            f"?token={raw_token}"
        )

        try:

            send_security_email(
                "EnglishNote staff invitation",
                (
                    f"You have been invited to join EnglishNote as {role}.\n\n"
                    f"Accept your invitation here:\n{link}\n\n"
                    "This invitation expires in 48 hours."
                ),
                email
            )

        except Exception:

            invitation.delete()

            return Response(
                {"message": "The invitation email could not be sent."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        return Response(
            {
                "message": "The invitation has been sent successfully.",
                "invitation_id": str(invitation.id),
            },
            status=status.HTTP_201_CREATED
        )


class AcceptInvitationView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        raw_token = request.data.get("token")

        username = request.data.get("username", "").strip()

        password = request.data.get("password")

        password_confirm = request.data.get("password_confirm")

        if not all([
            raw_token,
            username,
            password,
            password_confirm
        ]):

            return Response(
                {"message": "Please provide all required information."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if password != password_confirm:

            return Response(
                {"message": "The passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST
            )

        invitation = StaffInvitation.objects.filter(
            token_hash=hash_token(raw_token),
            status=StaffInvitation.Status.PENDING
        ).first()

        if not invitation or invitation.expires_at <= timezone.now():

            return Response(
                {"message": "This invitation is invalid or has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email__iexact=invitation.email).exists():

            return Response(
                {"message": "An account already exists with this email."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username__iexact=username).exists():

            return Response(
                {"message": "This username is already taken."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            validate_password(password)

        except Exception as error:

            return Response(
                {"message": " ".join(error.messages)},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():

            invitation = StaffInvitation.objects.select_for_update().get(
                pk=invitation.pk
            )

            if (
                invitation.status != StaffInvitation.Status.PENDING
                or invitation.expires_at <= timezone.now()
            ):

                return Response(
                    {"message": "This invitation is no longer available."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = User.objects.create_user(
                username=username,
                email=invitation.email,
                password=password,
                is_active=True,
                email_verified=True,
            )

            UserProfile.objects.get_or_create(user=user)

            RoleAssignment.objects.update_or_create(
                user=user,
                defaults={
                    "role": invitation.role,
                    "assigned_by": invitation.invited_by,
                }
            )

            invitation.status = StaffInvitation.Status.ACCEPTED

            invitation.accepted_by = user

            invitation.accepted_at = timezone.now()

            invitation.save()

        return Response({
            "message": (
                "Your invitation has been accepted. "
                "You can now sign in to your account."
            ),
            "role": invitation.role,
        }, status=status.HTTP_201_CREATED)