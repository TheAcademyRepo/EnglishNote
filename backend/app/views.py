from rest_framework import generics


from rest_framework.throttling import ScopedRateThrottle
from django.contrib.auth.tokens import default_token_generator

from .pagination import PostPagination

from django_filters.rest_framework import DjangoFilterBackend
from .filters import PostFilter
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Post, Category, Comment, PostLike, Note, Dailypost, Subject, Topic
from .serializers import (
    PostSerializer,
    CategorySerializer,
    TopicSerializer,
    CommentSerializer,
    SubjectSerializer,
    NoteSerializer,
    DailypostSerializer,
    RegisterSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    VerifyEmailSerializer,
    ResendVerificationSerializer
)

from django.contrib.auth.tokens import default_token_generator

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
import uuid
from rest_framework_simplejwt.tokens import RefreshToken



class LoginSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["username"] = user.username
        token["email"] = user.email

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "email_verified": self.user.email_verified,
        }

        return data


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_login"
    
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_register"

    def perform_create(self, serializer):
        user = serializer.save()

        token = default_token_generator.make_token(user)

        verification_link = (
            f"http://localhost:5173/verify-email/"
            f"?user_id={user.id}&token={token}"
        )

        send_mail(
            subject="Verify your EnglishNote account",
            message=(
                f"Welcome to EnglishNote!\n\n"
                f"Please verify your email by opening this link:\n\n"
                f"{verification_link}\n\n"
                f"If you did not create this account, "
                f"you can ignore this email."
            ),
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "email_verified": request.user.email_verified,
        })

class CategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TopicListView(generics.ListAPIView):
    serializer_class = TopicSerializer

    def get_queryset(self):
        queryset = Topic.objects.all()

        subject = self.request.query_params.get("subject")

        if subject:
            queryset = queryset.filter(subject_id=subject)

        return queryset
        
class SubjectList(generics.ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    
class NoteList(generics.ListAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

class DailypostList(generics.ListCreateAPIView):
    queryset = Dailypost.objects.all()
    serializer_class = DailypostSerializer
    
class DailypostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Dailypost.objects.all()
    serializer_class = DailypostSerializer
    lookup_field = "slug"
    
class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = PostFilter

    search_fields = [
        "title",
        "content",
        "category__title",
        "topic__title",
    ]

    ordering_fields = [
        "created_at",
        "title",
    ]

    ordering = [
        "-created_at"
    ]

    pagination_class = PostPagination
    
class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = PostFilter

    search_fields = [
        "title",
        "content",
    ]

    ordering_fields = [
        "created_at",
        "title",
    ]

    ordering = [
        "-created_at"
    ]

    pagination_class = PostPagination
    
    
    
    
    
    
class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = "slug"
    
    
    
    
class PostLikeView(APIView):

    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)

        # =========================
        # LOGGED-IN USER
        # =========================
        if request.user.is_authenticated:

            like = PostLike.objects.filter(
                post=post,
                user=request.user
            ).first()

            # Already liked → UNLIKE
            if like:
                like.delete()

                post.likes = max(0, post.likes - 1)
                post.save(update_fields=["likes"])

                return Response({
                    "liked": False,
                    "likes": post.likes
                })

            # Not liked → LIKE
            PostLike.objects.create(
                post=post,
                user=request.user
            )

            post.likes += 1
            post.save(update_fields=["likes"])

            return Response({
                "liked": True,
                "likes": post.likes
            })

        # =========================
        # ANONYMOUS VISITOR
        # =========================

        visitor_id = request.COOKIES.get("visitor_id")

        # First visit → create visitor ID
        if not visitor_id:
            visitor_id = str(uuid.uuid4())

        like = PostLike.objects.filter(
            post=post,
            visitor_id=visitor_id
        ).first()

        # Already liked → UNLIKE
        if like:
            like.delete()

            post.likes = max(0, post.likes - 1)
            post.save(update_fields=["likes"])

            response = Response({
                "liked": False,
                "likes": post.likes
            })

            response.set_cookie(
                "visitor_id",
                visitor_id,
                max_age=60 * 60 * 24 * 365
            )

            return response

        # Not liked → LIKE
        PostLike.objects.create(
            post=post,
            visitor_id=visitor_id
        )

        post.likes += 1
        post.save(update_fields=["likes"])

        response = Response({
            "liked": True,
            "likes": post.likes
        })

        response.set_cookie(
            "visitor_id",
            visitor_id,
            max_age=60 * 60 * 24 * 365
        )

        return response
        
        

    
class CommentListCreate(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        slug = self.kwargs["slug"]

        post = get_object_or_404(
            Post,
            slug=slug
        )

        return Comment.objects.filter(
            post=post,
            parent__isnull=True
        ).order_by("-created_at")

    def perform_create(self, serializer):
        slug = self.kwargs["slug"]

        post = get_object_or_404(
            Post,
            slug=slug
        )

        serializer.save(
            post=post
        )
        
        
class LogoutView(APIView):

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=400
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"detail": "Successfully logged out."},
                status=200
            )

        except Exception:
            return Response(
                {"detail": "Invalid refresh token."},
                status=400
            )
            
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "detail": "Password changed successfully."
        })
        
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_forgot_password"

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        User = get_user_model()
        user = User.objects.filter(email__iexact=email).first()

        if user:
            token = default_token_generator.make_token(user)

            reset_link = (
                f"http://localhost:5173/reset-password/"
                f"?user_id={user.id}&token={token}"
            )

            send_mail(
                subject="Reset your EnglishNote password",
                message=(
                    f"Hello {user.username},\n\n"
                    f"We received a request to reset your "
                    f"EnglishNote password.\n\n"
                    f"Reset your password here:\n\n"
                    f"{reset_link}\n\n"
                    f"If you did not request this, "
                    f"you can ignore this email."
                ),
                from_email=None,
                recipient_list=[user.email],
                fail_silently=False,
            )

        return Response({
            "detail": (
                "If an account with that email exists, "
                "reset instructions have been sent."
            )
        })


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_reset_password"

    def post(self, request):
        serializer = ResetPasswordSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "detail": "Password has been reset successfully."
        })
        
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_verify_email"

    def post(self, request):
        serializer = VerifyEmailSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "detail": "Email verified successfully."
        })
        
        
class ResendVerificationEmailView(APIView):
    permission_classes = [AllowAny]

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_resend_verification"

    def post(self, request):
        serializer = ResendVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        User = get_user_model()
        user = User.objects.filter(email__iexact=email).first()

        if user and not user.email_verified:
            token = default_token_generator.make_token(user)

            verification_link = (
                f"http://localhost:5173/verify-email/"
                f"?user_id={user.id}&token={token}"
            )

            send_mail(
                subject="Verify your EnglishNote account",
                message=(
                    f"Hello {user.username},\n\n"
                    f"Please verify your EnglishNote account "
                    f"by opening this link:\n\n"
                    f"{verification_link}\n\n"
                    f"If you did not create this account, "
                    f"you can ignore this email."
                ),
                from_email=None,
                recipient_list=[user.email],
                fail_silently=False,
            )

        return Response({
            "detail": (
                "If an unverified account with that email exists, "
                "a verification email has been sent."
            )
        })