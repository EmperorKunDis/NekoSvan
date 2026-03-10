"""Role-based permissions for API access control."""

import warnings

from rest_framework.permissions import BasePermission

from .models import User

# --- New semantic permission classes ---

class IsContractManager(BasePermission):
    """Contract management access (Adam / ADNP)."""

    ALLOWED_ROLES = [User.Role.ADAM]

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in self.ALLOWED_ROLES


class IsSalesLead(BasePermission):
    """Sales lead access (Vadim)."""

    ALLOWED_ROLES = [User.Role.VADIM]

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in self.ALLOWED_ROLES


class IsProjectManager(BasePermission):
    """Project management access (Martin / Praut)."""

    ALLOWED_ROLES = [User.Role.MARTIN]

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in self.ALLOWED_ROLES


class IsQAReviewer(BasePermission):
    """QA review access (Martin + NekoSvan)."""

    ALLOWED_ROLES = [User.Role.MARTIN, User.Role.NEKOSVAN]

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in self.ALLOWED_ROLES


# --- Deprecated: old name-based classes (emit DeprecationWarning) ---

class IsAdam(BasePermission):
    """Only Adam (ADNP) can access. Deprecated: use IsContractManager."""

    def has_permission(self, request, view):
        warnings.warn("IsAdam is deprecated, use IsContractManager", DeprecationWarning, stacklevel=2)
        return request.user.is_authenticated and request.user.role == User.Role.ADAM


class IsVadim(BasePermission):
    """Only Vadim can access. Deprecated: use IsSalesLead."""

    def has_permission(self, request, view):
        warnings.warn("IsVadim is deprecated, use IsSalesLead", DeprecationWarning, stacklevel=2)
        return request.user.is_authenticated and request.user.role == User.Role.VADIM


class IsMartin(BasePermission):
    """Only Martin (Praut) can access. Deprecated: use IsProjectManager."""

    def has_permission(self, request, view):
        warnings.warn("IsMartin is deprecated, use IsProjectManager", DeprecationWarning, stacklevel=2)
        return request.user.is_authenticated and request.user.role == User.Role.MARTIN


class IsNekoSvan(BasePermission):
    """Only NekoSvan can access. Deprecated: use IsQAReviewer."""

    def has_permission(self, request, view):
        warnings.warn("IsNekoSvan is deprecated, use IsQAReviewer", DeprecationWarning, stacklevel=2)
        return request.user.is_authenticated and request.user.role == User.Role.NEKOSVAN


# --- Generic permissions (unchanged) ---

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
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return request.user.role == User.Role.MARTIN


class IsQARole(BasePermission):
    """Only Martin or NekoSvan (QA roles) can access."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in (User.Role.MARTIN, User.Role.NEKOSVAN)
