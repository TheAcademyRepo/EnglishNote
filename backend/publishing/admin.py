from django.contrib import admin

from .models import ContentItem, ContentReview, ContentVersion


class ContentReviewInline(admin.TabularInline):

    model = ContentReview

    extra = 0

    readonly_fields = (
        "reviewer",
        "decision",
        "feedback",
        "created_at",
    )


class ContentVersionInline(admin.TabularInline):

    model = ContentVersion

    extra = 0

    readonly_fields = (
        "title",
        "body",
        "edited_by",
        "created_at",
    )


@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "content_type",
        "author",
        "status",
        "published_at",
        "created_at",
    )

    list_filter = (
        "content_type",
        "status",
        "created_at",
    )

    search_fields = (
        "title",
        "body",
        "author__username",
    )

    readonly_fields = (
        "slug",
        "views",
        "created_at",
        "updated_at",
        "published_at",
    )

    inlines = [
        ContentReviewInline,
        ContentVersionInline,
    ]


@admin.register(ContentReview)
class ContentReviewAdmin(admin.ModelAdmin):

    list_display = (
        "content",
        "reviewer",
        "decision",
        "created_at",
    )

    list_filter = (
        "decision",
        "created_at",
    )

    readonly_fields = (
        "created_at",
    )


@admin.register(ContentVersion)
class ContentVersionAdmin(admin.ModelAdmin):

    list_display = (
        "content",
        "edited_by",
        "created_at",
    )

    readonly_fields = (
        "created_at",
    )