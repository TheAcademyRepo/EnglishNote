from django.contrib.auth import get_user_model

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator

from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers
from .models import Post, Topic, Category, Comment, Note, Subject

User = get_user_model()





class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields =[
          "id",
          "name",
          "slug",
          "subject"
          ]



class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class PostSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(
        source="category.id",
        read_only=True
    )

    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    category_slug = serializers.CharField(
        source="category.slug",
        read_only=True
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "category_id",
            "category_name",
            "category_slug",
            "created_at",
            "image",
            "views",
            "likes",
        ]

        read_only_fields = [
            "likes",
        ]


class NoteSerializer(serializers.ModelSerializer):
    

    topic_id = serializers.PrimaryKeyRelatedField(
        queryset=Note.objects.all(),
        source="note",
        write_only=True
    )

    class Meta:
        model = Note
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "topic",
            "topic_id",
            "created_at",
            "image",
            "views",
            "likes",
        ]
        
class DailypostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "created_at",
            "views",
            "likes",
          ]
          
          
          
          
class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "parent",
            "name",
            "email",
            "content",
            "created_at",
            "replies",
        ]

        read_only_fields = [
            "id",
            "post",
            "created_at",
            "replies",
        ]

    def get_replies(self, obj):
        replies = obj.replies.all().order_by("created_at")
        return CommentSerializer(
            replies,
            many=True
        ).data
        
        
        
        
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "This username is already taken."
            )

        return value

    def validate_email(self, value):
        value = value.lower()

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"]
        )

        return user
        
        
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)

    new_password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    def validate_old_password(self, value):
        user = self.context["request"].user

        if not user.check_password(value):
            raise serializers.ValidationError(
                "Current password is incorrect."
            )

        return value

    def validate_new_password(self, value):
        user = self.context["request"].user

        validate_password(
            value,
            user=user
        )

        return value

    def save(self, **kwargs):
        user = self.context["request"].user

        user.set_password(
            self.validated_data["new_password"]
        )

        user.save()

        return user
        
        
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


        
class ResetPasswordSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    token = serializers.CharField()
    new_password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    def validate(self, data):
        User = get_user_model()

        try:
            user = User.objects.get(id=data["user_id"])
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "user_id": "Invalid user."
            })

        # Check the password-reset token
        if not default_token_generator.check_token(
            user,
            data["token"]
        ):
            raise serializers.ValidationError({
                "token": "Invalid or expired reset token."
            })

        # Check the new password against Django's
        # configured password validators
        validate_password(
            data["new_password"],
            user=user
        )

        data["user"] = user

        return data

    def save(self, **kwargs):
        user = self.validated_data["user"]

        user.set_password(
            self.validated_data["new_password"]
        )

        user.save()

        return user
        
        
class VerifyEmailSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    token = serializers.CharField()

    def validate(self, data):
        User = get_user_model()

        try:
            user = User.objects.get(id=data["user_id"])
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"user_id": "Invalid user."}
            )

        if not default_token_generator.check_token(
            user,
            data["token"]
        ):
            raise serializers.ValidationError(
                {"token": "Invalid or expired verification token."}
            )

        data["user"] = user
        return data

    def save(self, **kwargs):
        user = self.validated_data["user"]

        user.email_verified = True
        user.save(update_fields=["email_verified"])

        return user
        
class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()