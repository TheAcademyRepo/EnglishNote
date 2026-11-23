from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.exceptions import PermissionDenied, ValidationError

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)

from app.models import RoleAssignment, UserProfile
from app.roles import UserRole
from app.role_permissions import get_user_role

from .models import RoleInvitation

from .serializers import (
    RegistrationSerializer,
    SecureLoginSerializer,
    EmailSerializer,
    PasswordResetSerializer,
    ChangePasswordSerializer,
    AccountStatusSerializer,
)

from .services import (
    send_verification_email,
    send_password_reset_email,
)


User = get_user_model()


# ==========================================
# TOKEN REVOCATION
# ==========================================

def revoke_user_refresh_tokens(user):

    outstanding_tokens = OutstandingToken.objects.filter(
        user=user
    )

    for outstanding in outstanding_tokens:

        BlacklistedToken.objects.get_or_create(
            token=outstanding
        )


# ==========================================
# REGISTRATION
# ==========================================

class RegisterView(generics.CreateAPIView):

    serializer_class = RegistrationSerializer

    permission_classes = [
        permissions.AllowAny
    ]

    throttle_classes = [
        ScopedRateThrottle
    ]

    throttle_scope = "auth_register"

    def perform_create(self, serializer):

        user = serializer.save()

        send_verification_email(user)


# ==========================================
# LOGIN
# ==========================================

class LoginView(TokenObtainPairView):

    serializer_class = SecureLoginSerializer

    permission_classes = [
        permissions.AllowAny
    ]

    throttle_classes = [
        ScopedRateThrottle
    ]

    throttle_scope = "auth_login"


# ==========================================
# CURRENT USER
# ==========================================

class MeView(APIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request):

        user = request.user

        profile, created = UserProfile.objects.get_or_create(
            user=user
        )

        return Response({

            "id": user.id,

            "username": user.username,

            "email": user.email,

            "email_verified": user.email_verified,

            "role": get_user_role(user),

            "is_active": user.is_active,

            "profile": {
                "display_name": profile.display_name,
                "bio": profile.bio,
                "avatar_url": profile.avatar_url,
                "website": profile.website,
                "location": profile.location,
                "is_private": profile.is_private,
            },

        })


# ==========================================
# EMAIL VERIFICATION
# ==========================================

class VerifyEmailView(APIView):

    permission_classes = [
        permissions.AllowAny
    ]

    throttle_classes = [
        ScopedRateThrottle
    ]

    throttle_scope = "auth_verify_email"

    def post(self, request):

        user_id = request.data.get("user_id")

        token = request.data.get("token")

        user = get_object_or_404(
            User,
            id=user_id
        )

        if user.email_verified:

            return Response({
                "detail": "Your email is already verified."
            })

        if not default_token_generator.check_token(
            user,
            token
        ):

            return Response(
                {
                    "detail": "Invalid or expired verification link."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user.email_verified = True

        user.save(
            update_fields=["email_verified"]
        )

        return Response({
            "detail": "Email verified successfully."
        })


# ==========================================
# RESEND EMAIL VERIFICATION
# ==========================================

class ResendVerificationView(APIView):

    permission_classes = [
        permissions.AllowAny
    ]

    throttle_classes = [
        ScopedRateThrottle
    ]

    throttle_scope = "auth_resend_verification"

    def post(self, request):

        serializer = EmailSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        email = serializer.validated_data["email"]

        user = User.objects.filter(
            email__iexact=email
        ).first()

        if user and not user.email_verified:

            send_verification_email(user)

        return Response({
            "detail": (
                "If an unverified account exists, "
                "a verification email has been sent."
            )
        })


# ==========================================
# FORGOT PASSWORD
# ==========================================

class ForgotPasswordView(APIView):

    permission_classes = [
        permissions.AllowAny
    ]

    throttle_classes = [
        ScopedRateThrottle
    ]

    throttle_scope = "auth_forgot_password"

    def post(self, request):

        serializer = EmailSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = User.objects.filter(
            email__iexact=serializer.validated_data["email"]
        ).first()

        if user:

            send_password_reset_email(user)

        return Response({
            "detail": (
                "If an account with that email exists, "
                "password reset instructions have been sent."
            )
        })


# ==========================================
# RESET PASSWORD
# ==========================================

class ResetPasswordView(APIView):

    permission_classes = [
        permissions.AllowAny
    ]

    throttle_classes = [
        ScopedRateThrottle
    ]

    throttle_scope = "auth_reset_password"

    def post(self, request):

        serializer = PasswordResetSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.save()

        revoke_user_refresh_tokens(user)

        return Response({
            "detail": (
                "Password reset successfully. "
                "Please log in again."
            )
        })


# ==========================================
# CHANGE PASSWORD
# ==========================================

class ChangePasswordView(APIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def post(self, request):

        serializer = ChangePasswordSerializer(
            data=request.data,
            context={
                "request": request
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.save()

        revoke_user_refresh_tokens(user)

        return Response({
            "detail": (
                "Password changed successfully. "
                "Please log in again."
            )
        })


# ==========================================
# LOGOUT
# ==========================================

class LogoutView(APIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def post(self, request):

        refresh_token = request.data.get("refresh")

        if not refresh_token:

            return Response(
                {
                    "detail": "Refresh token is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            token = RefreshToken(refresh_token)

            if str(token["user_id"]) != str(request.user.id):

                return Response(
                    {
                        "detail": "Invalid refresh token."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            token.blacklist()

            return Response({
                "detail": "Successfully logged out."
            })

        except TokenError:

            return Response(
                {
                    "detail": "Invalid or expired refresh token."
                },
                status=status.HTTP_400_BAD_REQUEST
            )


# ==========================================
# CREATE ROLE INVITATION
# ==========================================

class CreateRoleInvitationView(APIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def post(self, request):

        role = get_user_role(request.user)

        allowed_roles = [
            UserRole.ADMINISTRATOR,
            UserRole.SUPER_ADMINISTRATOR,
        ]

        if role not in allowed_roles:

            raise PermissionDenied(
                "You cannot invite privileged users."
            )

        email = request.data.get("email")

        invited_role = request.data.get("role")

        allowed_invitation_roles = [
            UserRole.CONTRIBUTOR,
            UserRole.AUTHOR,
            UserRole.EDITOR,
            UserRole.ADMINISTRATOR,
        ]

        if invited_role not in allowed_invitation_roles:

            raise ValidationError({
                "role": "Invalid invitation role."
            })

        if (
            invited_role == UserRole.ADMINISTRATOR
            and role != UserRole.SUPER_ADMINISTRATOR
        ):

            raise PermissionDenied(
                "Only a Super Administrator can invite an Administrator."
            )

        if not email:

            raise ValidationError({
                "email": "Email is required."
            })

        email = email.strip().lower()

        existing_user = User.objects.filter(
            email__iexact=email
        ).first()

        if (
            existing_user
            and get_user_role(existing_user) != UserRole.STUDENT
        ):

            raise ValidationError({
                "email": (
                    "This account already has an assigned privileged role."
                )
            })

        raw_token = RoleInvitation.generate_token()

        invitation = RoleInvitation.objects.create(

            email=email,

            role=invited_role,

            token_hash=RoleInvitation.hash_token(
                raw_token
            ),

            created_by=request.user,

            expires_at=timezone.now() + timedelta(days=2),

        )

        frontend_url = getattr(
            settings,
            "FRONTEND_URL",
            "http://localhost:5173"
        ).rstrip("/")

        invitation_link = (
            f"{frontend_url}/accept-invitation/"
            f"?token={raw_token}"
        )

        try:

            send_mail(

                subject="EnglishNote role invitation",

                message=(
                    f"You have been invited to join EnglishNote "
                    f"as {invited_role}.\n\n"
                    f"Accept your invitation here:\n\n"
                    f"{invitation_link}\n\n"
                    f"This invitation expires in 48 hours."
                ),

                from_email=None,

                recipient_list=[email],

                fail_silently=False,

            )

        except Exception:

            invitation.status = RoleInvitation.Status.REVOKED

            invitation.save(
                update_fields=["status"]
            )

            raise

        return Response({

            "detail": "Invitation sent successfully.",

            "invitation_id": str(invitation.id),

            "expires_at": invitation.expires_at,

        }, status=status.HTTP_201_CREATED)


# ==========================================
# ACCEPT ROLE INVITATION
# ==========================================

class AcceptRoleInvitationView(APIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def post(self, request):

        raw_token = request.data.get("token")

        if not raw_token:

            raise ValidationError({
                "token": "Invitation token is required."
            })

        token_hash = RoleInvitation.hash_token(
            raw_token
        )

        with transaction.atomic():

            invitation = RoleInvitation.objects.select_for_update().filter(
                token_hash=token_hash
            ).first()

            if not invitation:

                raise ValidationError({
                    "detail": "Invalid invitation."
                })

            issuer_role = get_user_role(
                invitation.created_by
            )

            if issuer_role not in [
                UserRole.ADMINISTRATOR,
                UserRole.SUPER_ADMINISTRATOR,
            ]:

                invitation.status = RoleInvitation.Status.REVOKED

                invitation.save(
                    update_fields=["status"]
                )

                raise ValidationError({
                    "detail": "This invitation is no longer authorized."
                })

            if (
                invitation.role == UserRole.ADMINISTRATOR
                and issuer_role != UserRole.SUPER_ADMINISTRATOR
            ):

                invitation.status = RoleInvitation.Status.REVOKED

                invitation.save(
                    update_fields=["status"]
                )

                raise ValidationError({
                    "detail": "This invitation is no longer authorized."
                })

            if invitation.status != RoleInvitation.Status.PENDING:

                raise ValidationError({
                    "detail": "This invitation is no longer available."
                })

            if invitation.is_expired():

                invitation.status = RoleInvitation.Status.EXPIRED

                invitation.save(
                    update_fields=["status"]
                )

                raise ValidationError({
                    "detail": "This invitation has expired."
                })

            if request.user.email.lower() != invitation.email.lower():

                raise PermissionDenied(
                    "You must log in using the invited email address."
                )

            if not request.user.email_verified:

                raise PermissionDenied(
                    "Verify your email before accepting this invitation."
                )

            if get_user_role(request.user) != UserRole.STUDENT:

                raise ValidationError({
                    "detail": "This account already has a privileged role."
                })

            RoleAssignment.objects.update_or_create(

                user=request.user,

                defaults={
                    "role": invitation.role,
                    "assigned_by": invitation.created_by,
                }

            )

            invitation.status = RoleInvitation.Status.ACCEPTED

            invitation.accepted_by = request.user

            invitation.accepted_at = timezone.now()

            invitation.save(
                update_fields=[
                    "status",
                    "accepted_by",
                    "accepted_at",
                ]
            )

        return Response({

            "detail": "Your invitation was accepted successfully.",

            "role": invitation.role,

        })


# ==========================================
# ADMIN ROLE MANAGEMENT
# ==========================================

class ManageUserRoleView(APIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def patch(self, request, user_id):

        actor_role = get_user_role(request.user)

        target = get_object_or_404(
            User,
            id=user_id
        )

        new_role = request.data.get("role")

        if actor_role not in [
            UserRole.ADMINISTRATOR,
            UserRole.SUPER_ADMINISTRATOR,
        ]:

            raise PermissionDenied(
                "You cannot manage user roles."
            )

        if new_role not in UserRole.all():

            raise ValidationError({
                "role": "Invalid role."
            })

        target_role = get_user_role(target)

        if (
            target.is_superuser
            or target_role == UserRole.SUPER_ADMINISTRATOR
        ):

            raise PermissionDenied(
                "Super Administrator accounts cannot be modified here."
            )

        if (
            target_role == UserRole.ADMINISTRATOR
            and actor_role != UserRole.SUPER_ADMINISTRATOR
        ):

            raise PermissionDenied(
                "Only a Super Administrator can modify an Administrator account."
            )

        if (
            new_role == UserRole.ADMINISTRATOR
            and actor_role != UserRole.SUPER_ADMINISTRATOR
        ):

            raise PermissionDenied(
                "Only a Super Administrator can assign Administrator."
            )

        if new_role == UserRole.SUPER_ADMINISTRATOR:

            raise PermissionDenied(
                "Super Administrator status cannot be assigned through this endpoint."
            )

        if target.id == request.user.id:

            raise ValidationError({
                "detail": "You cannot change your own role here."
            })

        assignment, created = RoleAssignment.objects.update_or_create(

            user=target,

            defaults={
                "role": new_role,
                "assigned_by": request.user,
            }

        )

        return Response({

            "detail": "User role updated successfully.",

            "user_id": target.id,

            "role": assignment.role,

        })


# ==========================================
# ACCOUNT ACTIVATION / DEACTIVATION
# ==========================================

class ManageUserAccountView(APIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def patch(self, request, user_id):

        actor_role = get_user_role(request.user)

        if actor_role not in [
            UserRole.ADMINISTRATOR,
            UserRole.SUPER_ADMINISTRATOR,
        ]:

            raise PermissionDenied(
                "Permission denied."
            )

        target = get_object_or_404(
            User,
            id=user_id
        )

        target_role = get_user_role(target)

        if (
            target.is_superuser
            or target_role == UserRole.SUPER_ADMINISTRATOR
        ):

            raise PermissionDenied(
                "Super Administrator accounts cannot be modified here."
            )

        if (
            target_role == UserRole.ADMINISTRATOR
            and actor_role != UserRole.SUPER_ADMINISTRATOR
        ):

            raise PermissionDenied(
                "Only a Super Administrator can modify an Administrator account."
            )

        if target.id == request.user.id:

            raise ValidationError({
                "detail": "You cannot deactivate your own account here."
            })

        serializer = AccountStatusSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        target.is_active = serializer.validated_data[
            "is_active"
        ]

        target.save(
            update_fields=["is_active"]
        )

        if not target.is_active:

            revoke_user_refresh_tokens(target)

        return Response({

            "detail": "Account status updated.",

            "is_active": target.is_active,

        })