from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    crm_access = models.BooleanField(default=False)
    last_online_at = models.DateTimeField(null=True, blank=True)
    current_crm_team = models.ForeignKey(
        'accounts.CRMTeam',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_users'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return self.email


class Permission(models.Model):
    name = models.CharField(max_length=255)
    guard_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'permissions'
        unique_together = [['name', 'guard_name']]
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Role(models.Model):
    team = models.ForeignKey(
        'accounts.Team',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='roles'
    )
    name = models.CharField(max_length=255)
    guard_name = models.CharField(max_length=255)
    permissions = models.ManyToManyField(
        Permission,
        through='RoleHasPermission',
        related_name='roles'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roles'
        unique_together = [['team', 'name', 'guard_name']]
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ModelHasPermission(models.Model):
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='model_permissions'
    )
    model_type = models.CharField(max_length=255)
    model_id = models.BigIntegerField()
    team = models.ForeignKey(
        'accounts.Team',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='model_permissions'
    )

    class Meta:
        db_table = 'model_has_permissions'
        indexes = [
            models.Index(fields=['model_id', 'model_type']),
        ]

    def __str__(self):
        return f"{self.model_type}:{self.model_id} - {self.permission.name}"


class ModelHasRole(models.Model):
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='model_roles'
    )
    model_type = models.CharField(max_length=255)
    model_id = models.BigIntegerField()
    team = models.ForeignKey(
        'accounts.Team',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='model_roles'
    )

    class Meta:
        db_table = 'model_has_roles'
        indexes = [
            models.Index(fields=['model_id', 'model_type']),
        ]

    def __str__(self):
        return f"{self.model_type}:{self.model_id} - {self.role.name}"


class RoleHasPermission(models.Model):
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='permission_roles'
    )

    class Meta:
        db_table = 'role_has_permissions'
        unique_together = [['permission', 'role']]

    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"


class Team(models.Model):
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    guard_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'teams'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class CRMTeam(models.Model):
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='crm_teams_owned'
    )
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'crm_teams'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class CRMTeamUser(models.Model):
    crm_team = models.ForeignKey(
        CRMTeam,
        on_delete=models.CASCADE,
        related_name='members'
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='crm_team_memberships'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crm_team_user'
        unique_together = [['crm_team', 'user']]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.crm_team.name}"


class CRMTeamInvitation(models.Model):
    crm_team = models.ForeignKey(
        CRMTeam,
        on_delete=models.CASCADE,
        related_name='invitations'
    )
    email = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crm_team_invitations'
        unique_together = [['crm_team', 'email']]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} - {self.crm_team.name}"


class Device(models.Model):
    """Tracks user devices for security/analytics."""
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='devices'
    )
    platform = models.CharField(max_length=255, null=True, blank=True)
    platform_version = models.CharField(max_length=255, null=True, blank=True)
    browser = models.CharField(max_length=255, null=True, blank=True)
    browser_version = models.CharField(max_length=255, null=True, blank=True)
    is_desktop = models.BooleanField(default=False)
    is_mobile = models.BooleanField(default=False)
    language = models.CharField(max_length=255, null=True, blank=True)
    is_trusted = models.BooleanField(default=False, db_index=True)
    is_untrusted = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'devices'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.browser} on {self.platform}"


class Login(models.Model):
    """Tracks user login history."""
    TYPE_LOGIN = 'login'
    TYPE_LOGOUT = 'logout'
    TYPE_FAILED = 'failed'
    TYPE_CHOICES = [
        (TYPE_LOGIN, 'Login'),
        (TYPE_LOGOUT, 'Logout'),
        (TYPE_FAILED, 'Failed'),
    ]

    ip_address = models.GenericIPAddressField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_LOGIN)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='logins'
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logins',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'logins'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.type} from {self.ip_address}"
