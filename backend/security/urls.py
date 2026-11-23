from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    VerifyEmailView,
    ResendVerificationView,
    LoginView,
    LogoutView,
    MeView,
    ForgotPasswordView,
    ResetPasswordView,
    ChangePasswordView,
    CreateInvitationView,
    AcceptInvitationView,
)


urlpatterns = [

    path("register/", RegisterView.as_view()),

    path("verify-email/", VerifyEmailView.as_view()),

    path(
        "resend-verification/",
        ResendVerificationView.as_view()
    ),

    path("login/", LoginView.as_view()),

    path("refresh/", TokenRefreshView.as_view()),

    path("logout/", LogoutView.as_view()),

    path("me/", MeView.as_view()),

    path("forgot-password/", ForgotPasswordView.as_view()),

    path("reset-password/", ResetPasswordView.as_view()),

    path("change-password/", ChangePasswordView.as_view()),

    path("invitations/create/", CreateInvitationView.as_view()),

    path("invitations/accept/", AcceptInvitationView.as_view()),

]