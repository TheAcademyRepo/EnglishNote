from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import BasePermission

from .roles import UserRole


def get_user_role(user):
    if not user or not user.is_authenticated:
        return None
    if getattr(user, "is_superuser", False):
        return UserRole.SUPER_ADMINISTRATOR
    try:
        return user.role_assignment.role
    except ObjectDoesNotExist:
        return UserRole.STUDENT


def has_role(user, allowed_roles):
    return get_user_role(user) in allowed_roles


def is_authorized_administrator(user):
    return has_role(user, [UserRole.ADMINISTRATOR, UserRole.SUPER_ADMINISTRATOR])


def can_create_content(user):
    return has_role(user, [UserRole.AUTHOR, UserRole.ADMINISTRATOR, UserRole.SUPER_ADMINISTRATOR])


def can_submit_content(user):
    return has_role(user, [UserRole.CONTRIBUTOR, UserRole.AUTHOR, UserRole.ADMINISTRATOR, UserRole.SUPER_ADMINISTRATOR])


def can_manage_topics_and_lessons(user):
    return has_role(user, [UserRole.EDITOR, UserRole.AUTHOR, UserRole.ADMINISTRATOR, UserRole.SUPER_ADMINISTRATOR])


def can_moderate_content(user):
    return has_role(user, [UserRole.AUTHOR, UserRole.EDITOR, UserRole.ADMINISTRATOR, UserRole.SUPER_ADMINISTRATOR])


class IsStudentOrHigher(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsContributor(BasePermission):
    def has_permission(self, request, view):
        return has_role(request.user, [UserRole.CONTRIBUTOR])


class IsAuthor(BasePermission):
    def has_permission(self, request, view):
        return has_role(request.user, [UserRole.AUTHOR, UserRole.ADMINISTRATOR, UserRole.SUPER_ADMINISTRATOR])


class IsEditor(BasePermission):
    def has_permission(self, request, view):
        return has_role(request.user, [UserRole.EDITOR, UserRole.ADMINISTRATOR, UserRole.SUPER_ADMINISTRATOR])


class IsAdministrator(BasePermission):
    def has_permission(self, request, view):
        return is_authorized_administrator(request.user)


class IsSuperAdministrator(BasePermission):
    def has_permission(self, request, view):
        return get_user_role(request.user) == UserRole.SUPER_ADMINISTRATOR
