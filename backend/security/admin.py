from django.contrib import admin

from .models import SecurityToken, StaffInvitation


@admin.register(SecurityToken)
class SecurityTokenAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "token_type",
        "expires_at",
        "used_at",
        "created_at",
    )

    search_fields = (
        "user__email",
        "user__username",
    )

    list_filter = (
        "token_type",
        "created_at",
    )

    readonly_fields = (
        "token_hash",
        "created_at",
    )


@admin.register(StaffInvitation)
class StaffInvitationAdmin(admin.ModelAdmin):

    list_display = (
        "email",
        "role",
        "status",
        "invited_by",
        "expires_at",
    )

    search_fields = (
        "email",
    )

    list_filter = (
        "role",
        "status",
    )

    readonly_fields = (
        "token_hash",
        "created_at",
        "accepted_at",
    )

    def has_add_permission(self, request):
        return False