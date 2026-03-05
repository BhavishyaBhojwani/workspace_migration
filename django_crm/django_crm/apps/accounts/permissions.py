"""
Custom permission classes for the CRM.
Implements team-based and role-based permissions similar to Laravel's Spatie Permission.
"""
from django.contrib.contenttypes.models import ContentType
from rest_framework import permissions

from .models import ModelHasPermission, ModelHasRole, CRMTeamUser


class HasPermission(permissions.BasePermission):
    """
    Check if user has a specific permission.
    Set required_permission on the view class.
    """
    message = 'You do not have permission to perform this action.'

    def has_permission(self, request, view):
        required_permission = getattr(view, 'required_permission', None)
        
        if not required_permission:
            return True
        
        if not request.user.is_authenticated:
            return False
        
        # Superusers have all permissions
        if request.user.is_superuser:
            return True
        
        return self._user_has_permission(request.user, required_permission)

    def _user_has_permission(self, user, permission_name):
        """Check if user has permission directly or through roles."""
        content_type = ContentType.objects.get_for_model(user)
        
        # Check direct permissions
        direct_perm = ModelHasPermission.objects.filter(
            model_type=content_type.model,
            model_id=user.id,
            permission__name=permission_name
        ).exists()
        
        if direct_perm:
            return True
        
        # Check role permissions
        user_roles = ModelHasRole.objects.filter(
            model_type=content_type.model,
            model_id=user.id
        ).select_related('role')
        
        for model_role in user_roles:
            if model_role.role.permissions.filter(name=permission_name).exists():
                return True
        
        return False


class HasAnyPermission(permissions.BasePermission):
    """
    Check if user has any of the specified permissions.
    Set required_permissions (list) on the view class.
    """
    message = 'You do not have permission to perform this action.'

    def has_permission(self, request, view):
        required_permissions = getattr(view, 'required_permissions', [])
        
        if not required_permissions:
            return True
        
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        for perm in required_permissions:
            if HasPermission()._user_has_permission(request.user, perm):
                return True
        
        return False


class HasAllPermissions(permissions.BasePermission):
    """
    Check if user has all of the specified permissions.
    Set required_permissions (list) on the view class.
    """
    message = 'You do not have all required permissions.'

    def has_permission(self, request, view):
        required_permissions = getattr(view, 'required_permissions', [])
        
        if not required_permissions:
            return True
        
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        for perm in required_permissions:
            if not HasPermission()._user_has_permission(request.user, perm):
                return False
        
        return True


class HasRole(permissions.BasePermission):
    """
    Check if user has a specific role.
    Set required_role on the view class.
    """
    message = 'You do not have the required role.'

    def has_permission(self, request, view):
        required_role = getattr(view, 'required_role', None)
        
        if not required_role:
            return True
        
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        content_type = ContentType.objects.get_for_model(request.user)
        
        return ModelHasRole.objects.filter(
            model_type=content_type.model,
            model_id=request.user.id,
            role__name=required_role
        ).exists()


class IsTeamOwner(permissions.BasePermission):
    """
    Check if user is the owner of the team.
    """
    message = 'Only team owner can perform this action.'

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Handle CRMTeam objects
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Handle objects with team relationship
        if hasattr(obj, 'crm_team'):
            return obj.crm_team.user == request.user
        
        return False


class IsTeamMember(permissions.BasePermission):
    """
    Check if user is a member of the team.
    """
    message = 'You must be a team member to perform this action.'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Check if user has a current team
        return request.user.current_crm_team is not None

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        team = None
        
        # Get team from object
        if hasattr(obj, 'id') and hasattr(obj, 'members'):  # CRMTeam
            team = obj
        elif hasattr(obj, 'crm_team'):
            team = obj.crm_team
        
        if not team:
            return False
        
        return CRMTeamUser.objects.filter(
            crm_team=team,
            user=request.user
        ).exists()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any authenticated request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for owners
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        return False


class IsCRMUser(permissions.BasePermission):
    """
    Check if user has CRM access.
    """
    message = 'CRM access is required.'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.crm_access


class TeamPermission(permissions.BasePermission):
    """
    Team-scoped permission check.
    Verifies user has permission within their current team context.
    """
    message = 'You do not have team permission for this action.'

    def has_permission(self, request, view):
        required_permission = getattr(view, 'required_permission', None)
        
        if not required_permission:
            return True
        
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        team = request.user.current_crm_team
        if not team:
            return False
        
        content_type = ContentType.objects.get_for_model(request.user)
        
        # Check team-scoped permissions
        return ModelHasPermission.objects.filter(
            model_type=content_type.model,
            model_id=request.user.id,
            permission__name=required_permission,
            team=team
        ).exists() or ModelHasRole.objects.filter(
            model_type=content_type.model,
            model_id=request.user.id,
            role__permissions__name=required_permission,
            team=team
        ).exists()


# ========================
# PERMISSION MIXINS
# ========================

class PermissionMixin:
    """
    Mixin to add permission checking methods to views.
    Similar to Laravel's HasRoles trait.
    """
    
    def user_has_permission(self, user, permission_name, team=None):
        """Check if user has a specific permission."""
        if user.is_superuser:
            return True
        
        content_type = ContentType.objects.get_for_model(user)
        
        # Check direct permission
        query = ModelHasPermission.objects.filter(
            model_type=content_type.model,
            model_id=user.id,
            permission__name=permission_name
        )
        if team:
            query = query.filter(team=team)
        
        if query.exists():
            return True
        
        # Check role permissions
        role_query = ModelHasRole.objects.filter(
            model_type=content_type.model,
            model_id=user.id,
            role__permissions__name=permission_name
        )
        if team:
            role_query = role_query.filter(team=team)
        
        return role_query.exists()

    def user_has_role(self, user, role_name, team=None):
        """Check if user has a specific role."""
        if user.is_superuser:
            return True
        
        content_type = ContentType.objects.get_for_model(user)
        
        query = ModelHasRole.objects.filter(
            model_type=content_type.model,
            model_id=user.id,
            role__name=role_name
        )
        if team:
            query = query.filter(team=team)
        
        return query.exists()

    def get_user_permissions(self, user, team=None):
        """Get all permissions for a user."""
        content_type = ContentType.objects.get_for_model(user)
        permissions = set()
        
        # Direct permissions
        direct_query = ModelHasPermission.objects.filter(
            model_type=content_type.model,
            model_id=user.id
        ).select_related('permission')
        if team:
            direct_query = direct_query.filter(team=team)
        
        for mp in direct_query:
            permissions.add(mp.permission.name)
        
        # Role permissions
        role_query = ModelHasRole.objects.filter(
            model_type=content_type.model,
            model_id=user.id
        ).select_related('role')
        if team:
            role_query = role_query.filter(team=team)
        
        for mr in role_query:
            for perm in mr.role.permissions.all():
                permissions.add(perm.name)
        
        return list(permissions)

    def get_user_roles(self, user, team=None):
        """Get all roles for a user."""
        content_type = ContentType.objects.get_for_model(user)
        
        query = ModelHasRole.objects.filter(
            model_type=content_type.model,
            model_id=user.id
        ).select_related('role')
        if team:
            query = query.filter(team=team)
        
        return [mr.role.name for mr in query]

