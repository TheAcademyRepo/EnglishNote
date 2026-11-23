from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    LoginView,
    MeView,
    VerifyEmailView,
    ResendVerificationView,
    ForgotPasswordView,
    ResetPasswordView,
    ChangePasswordView,
    LogoutView,
    CreateRoleInvitationView,
    AcceptRoleInvitationView,
    ManageUserRoleView,
    ManageUserAccountView,
)


urlpatterns = [

    path(
        "register/",
        RegisterView.as_view()
    ),

    path(
        "login/",
        LoginView.as_view()
    ),

    path(
        "refresh/",
        TokenRefreshView.as_view()
    ),

    path(
        "me/",
        MeView.as_view()
    ),

    path(
        "verify-email/",
        VerifyEmailView.as_view()
    ),

    path(
        "resend-verification/",
        ResendVerificationView.as_view()
    ),

    path(
        "forgot-password/",
        ForgotPasswordView.as_view()
    ),

    path(
        "reset-password/",
        ResetPasswordView.as_view()
    ),

    path(
        "change-password/",
        ChangePasswordView.as_view()
    ),

    path(
        "logout/",
        LogoutView.as_view()
    ),

    path(
        "invitations/create/",
        CreateRoleInvitationView.as_view()
    ),

    path(
        "invitations/accept/",
        AcceptRoleInvitationView.as_view()
    ),

    path(
        "users/<int:user_id>/role/",
        ManageUserRoleView.as_view()
    ),

    path(
        "users/<int:user_id>/account/",
        ManageUserAccountView.as_view()
    ),

]