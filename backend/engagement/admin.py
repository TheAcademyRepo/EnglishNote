from django.contrib import admin

from .models import (
    Like,
    Bookmark,
    Share,
    Comment,
    Report,
)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "content",
        "created_at",
    )

    search_fields = (
        "user__username",
        "content__title",
    )

    readonly_fields = (
        "created_at",
    )


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "content",
        "created_at",
    )

    search_fields = (
        "user__username",
        "content__title",
    )


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):

    list_display = (
        "content",
        "user",
        "platform",
        "created_at",
    )

    list_filter = (
        "platform",
        "created_at",
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "content",
        "is_hidden",
        "created_at",
    )

    list_filter = (
        "is_hidden",
        "created_at",
    )

    search_fields = (
        "body",
        "user__username",
        "content__title",
    )


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):

    list_display = (
        "reporter",
        "target_type",
        "reason",
        "status",
        "reviewed_by",
        "created_at",
    )

    list_filter = (
        "target_type",
        "reason",
        "status",
    )

    search_fields = (
        "reporter__username",
        "description",
    )

    readonly_fields = (
        "created_at",
        "reviewed_at",
    )