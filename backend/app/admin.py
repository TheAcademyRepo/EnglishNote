from django.contrib import admin

from .models import (
    Post,
    Category,
    Topic,
    Note,
    Subject,
    Dailypost,
    Comment,
)

from .role_models import (
    UserProfile,
    RoleAssignment,
)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "created_at", "views", "likes")
    search_fields = ("title",)
    list_filter = ("category", "created_at")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("name", "subject")
    search_fields = ("name",)
    list_filter = ("subject",)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("title", "topic", "created_at", "views", "likes")
    search_fields = ("title",)
    list_filter = ("topic", "created_at")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("title", "slug")
    search_fields = ("title",)


@admin.register(Dailypost)
class DailypostAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "views", "likes")
    search_fields = ("title",)
    list_filter = ("created_at",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("name", "post", "created_at")
    search_fields = ("name", "email", "content")
    list_filter = ("created_at",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "is_private", "created_at")
    search_fields = ("user__username", "user__email", "display_name")
    list_filter = ("is_private",)


@admin.register(RoleAssignment)
class RoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "assigned_by", "assigned_at")
    search_fields = ("user__username", "user__email")
    list_filter = ("role",)
    readonly_fields = ("assigned_at", "updated_at")