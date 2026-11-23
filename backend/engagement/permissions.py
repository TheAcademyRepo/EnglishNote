from rest_framework.permissions import BasePermission

from app.roles import UserRole
from app.role_permissions import get_user_role


class IsContentModerator(BasePermission):

    def has_permission(self, request, view):

        return get_user_role(request.user) in [
            UserRole.AUTHOR,
            UserRole.EDITOR,
            UserRole.ADMINISTRATOR,
            UserRole.SUPER_ADMINISTRATOR,
        ]


class IsReportAdministrator(BasePermission):

    def has_permission(self, request, view):

        return get_user_role(request.user) in [
            UserRole.ADMINISTRATOR,
            UserRole.SUPER_ADMINISTRATOR,
        ]