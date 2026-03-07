"""Role-based permissions for API access control."""

from rest_framework.permissions import BasePermission

from .models import User


class IsAdam(BasePermission):
    """Only Adam (ADNP) can access."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.ADAM


class IsVadim(BasePermission):
    """Only Vadim can access."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.VADIM


class IsMartin(BasePermission):
    """Only Martin (Praut) can access."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.MARTIN


class IsNekoSvan(BasePermission):
    """Only NekoSvan can access."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.NEKOSVAN


class IsInternalUser(BasePermission):
    """Any internal user (not client role)."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role != User.Role.CLIENT


class DealPhasePermission(BasePermission):
    """Any internal user can read/write deals in any phase."""

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.role != User.Role.CLIENT


class ProposalPermission(BasePermission):
    """Any internal user can create/edit proposals."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role != User.Role.CLIENT


class ContractPermission(BasePermission):
    """Any internal user can create/edit contracts."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role != User.Role.CLIENT


class PaymentPermission(BasePermission):
    """Any internal user can manage payments."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role != User.Role.CLIENT


class MilestoneActionPermission(BasePermission):
    """Any internal user can perform milestone actions."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role != User.Role.CLIENT


class IsMartinRole(BasePermission):
    """Only Martin (Praut) can modify; others can read."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role == User.Role.CLIENT:
            return False
        # Read-only for non-Martin users
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return request.user.role == User.Role.MARTIN


class IsQARole(BasePermission):
    """Only Martin or NekoSvan (QA roles) can access."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in (User.Role.MARTIN, User.Role.NEKOSVAN)
