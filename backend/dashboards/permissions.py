from rest_framework.permissions import BasePermission

from app.roles import UserRole
from app.role_permissions import get_user_role


class IsDashboardUser(BasePermission):

    def has_permission(self, request, view):

        return (
            request.user
            and request.user.is_authenticated
        )


class IsAuthorOrHigher(BasePermission):

    def has_permission(self, request, view):

        role = get_user_role(request.user)

        return role in [
            UserRole.AUTHOR,
            UserRole.ADMINISTRATOR,
            UserRole.SUPER_ADMINISTRATOR,
        ]


class IsEditorOrHigher(BasePermission):

    def has_permission(self, request, view):

        role = get_user_role(request.user)

        return role in [
            UserRole.EDITOR,
            UserRole.ADMINISTRATOR,
            UserRole.SUPER_ADMINISTRATOR,
        ]


class IsAdministratorOrHigher(BasePermission):

    def has_permission(self, request, view):

        role = get_user_role(request.user)

        return role in [
            UserRole.ADMINISTRATOR,
            UserRole.SUPER_ADMINISTRATOR,
        ]