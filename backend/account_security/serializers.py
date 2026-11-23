from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from app.models import UserProfile, RoleAssignment
from app.roles import UserRole
from rest_framework import serializers


User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )

    password_confirmation = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User

        fields = [
            "username",
            "email",
            "password",
            "password_confirmation",
        ]

    def validate_email(self, value):

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return value

    def validate(self, attrs):

        if attrs["password"] != attrs["password_confirmation"]:
            raise serializers.ValidationError({
                "password_confirmation": "Passwords do not match."
            })

        return attrs

    def create(self, validated_data):

        validated_data.pop("password_confirmation")
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            email=validated_data["email"],
            username=validated_data["username"],
            email_verified=False,
            is_active=True,
        )

        RoleAssignment.objects.update_or_create(
            user=user,
            defaults={
                "role": UserRole.STUDENT,
                "assigned_by": None,
            }
        )

        UserProfile.objects.get_or_create(user=user)

        return user


class SecureLoginSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):

        token = super().get_token(user)

        token["username"] = user.username
        token["email"] = user.email

        return token

    def validate(self, attrs):

        data = super().validate(attrs)

        if not self.user.email_verified:
            raise serializers.ValidationError({
                "detail": "Please verify your email before logging in.",
                "code": "email_not_verified",
            })

        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "email_verified": self.user.email_verified,
        }

        return data


class EmailSerializer(serializers.Serializer):

    email = serializers.EmailField()


class PasswordResetSerializer(serializers.Serializer):

    user_id = serializers.IntegerField()

    token = serializers.CharField()

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )

    password_confirmation = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):

        if attrs["password"] != attrs["password_confirmation"]:
            raise serializers.ValidationError({
                "password_confirmation": "Passwords do not match."
            })

        user = User.objects.filter(
            id=attrs["user_id"]
        ).first()

        if not user:
            raise serializers.ValidationError(
                "Invalid password reset request."
            )

        if not default_token_generator.check_token(
            user,
            attrs["token"]
        ):
            raise serializers.ValidationError(
                "This password reset link is invalid or expired."
            )

        attrs["user"] = user

        return attrs

    def save(self):

        user = self.validated_data["user"]

        user.set_password(
            self.validated_data["password"]
        )

        user.save(update_fields=["password"])

        return user


class ChangePasswordSerializer(serializers.Serializer):

    current_password = serializers.CharField(
        write_only=True
    )

    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )

    new_password_confirmation = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):

        user = self.context["request"].user

        if not user.check_password(attrs["current_password"]):
            raise serializers.ValidationError({
                "current_password": "Your current password is incorrect."
            })

        if attrs["new_password"] != attrs["new_password_confirmation"]:
            raise serializers.ValidationError({
                "new_password_confirmation": "Passwords do not match."
            })

        return attrs

    def save(self):

        user = self.context["request"].user

        user.set_password(
            self.validated_data["new_password"]
        )

        user.save(update_fields=["password"])

        return user


class AccountStatusSerializer(serializers.Serializer):

    is_active = serializers.BooleanField()
    
    
    
class AccountStatusSerializer(serializers.Serializer):

    is_active = serializers.BooleanField(
        required=True
    )