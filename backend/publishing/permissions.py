from rest_framework.permissions import BasePermission

from app.roles import UserRole
from app.role_permissions import get_user_role


class CanCreateContent(BasePermission):

    def has_permission(self, request, view):

        return get_user_role(request.user) in [
            UserRole.CONTRIBUTOR,
            UserRole.AUTHOR,
            UserRole.ADMINISTRATOR,
            UserRole.SUPER_ADMINISTRATOR,
        ]


class CanPublishContent(BasePermission):

    def has_permission(self, request, view):

        return get_user_role(request.user) in [
            UserRole.AUTHOR,
            UserRole.ADMINISTRATOR,
            UserRole.SUPER_ADMINISTRATOR,
        ]


class CanReviewContent(BasePermission):

    def has_permission(self, request, view):

        return get_user_role(request.user) in [
            UserRole.AUTHOR,
            UserRole.EDITOR,
            UserRole.ADMINISTRATOR,
            UserRole.SUPER_ADMINISTRATOR,
        ]


class CanManageTopics(BasePermission):

    def has_permission(self, request, view):

        return get_user_role(request.user) in [
            UserRole.EDITOR,
            UserRole.AUTHOR,
            UserRole.ADMINISTRATOR,
            UserRole.SUPER_ADMINISTRATOR,
        ]


class CanManageSubjects(BasePermission):

    def has_permission(self, request, view):

        return get_user_role(request.user) in [
            UserRole.ADMINISTRATOR,
            UserRole.SUPER_ADMINISTRATOR,
        ]