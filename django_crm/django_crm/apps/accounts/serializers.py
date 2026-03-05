"""
Authentication and Account Serializers.
Replicates Laravel Breeze + Sanctum authentication patterns.
"""
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import (
    CRMTeam, CRMTeamUser, CRMTeamInvitation, Device, Login,
    Role, Permission, ModelHasRole
)


User = get_user_model()


# ========================
# USER SERIALIZERS
# ========================

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user information."""
    current_team = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'crm_access', 'email_verified_at',
            'last_online_at', 'current_team', 'roles', 'permissions',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'email_verified_at', 'created_at', 'updated_at']

    def get_current_team(self, obj):
        if obj.current_crm_team:
            return CRMTeamSerializer(obj.current_crm_team).data
        return None

    def get_roles(self, obj):
        """Get user's roles from ModelHasRole."""
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(User)
        model_roles = ModelHasRole.objects.filter(
            model_type=content_type.model,
            model_id=obj.id
        ).select_related('role')
        return [mr.role.name for mr in model_roles]

    def get_permissions(self, obj):
        """Get user's permissions from roles."""
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(User)
        model_roles = ModelHasRole.objects.filter(
            model_type=content_type.model,
            model_id=obj.id
        ).select_related('role')
        
        permissions = set()
        for mr in model_roles:
            for perm in mr.role.permissions.all():
                permissions.add(perm.name)
        return list(permissions)


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    class Meta:
        model = User
        fields = ['name', 'email']

    def validate_email(self, value):
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value


# ========================
# AUTHENTICATION SERIALIZERS
# ========================

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration (similar to Laravel Breeze)."""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirmation = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'password_confirmation']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirmation']:
            raise serializers.ValidationError({
                'password_confirmation': "Password fields don't match."
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirmation')
        password = validated_data.pop('password')
        
        user = User.objects.create(
            username=validated_data['email'],  # Use email as username
            crm_access=True,  # Enable CRM access by default
            **validated_data
        )
        user.set_password(password)
        user.save()
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login (similar to Laravel Breeze)."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    remember = serializers.BooleanField(default=False, required=False)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError({
                'email': 'Invalid credentials provided.'
            })

        if not user.is_active:
            raise serializers.ValidationError({
                'email': 'User account is disabled.'
            })

        attrs['user'] = user
        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with additional claims."""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['name'] = user.name
        token['email'] = user.email
        token['crm_access'] = user.crm_access
        if user.current_crm_team:
            token['current_team_id'] = user.current_crm_team.id
        
        return token


class TokenRefreshSerializer(serializers.Serializer):
    """Serializer for refreshing tokens."""
    refresh = serializers.CharField(required=True)


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing password."""
    current_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirmation = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirmation']:
            raise serializers.ValidationError({
                'new_password_confirmation': "Password fields don't match."
            })
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting password reset."""
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            # Don't reveal if email exists or not
            pass
        return value


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for resetting password with token."""
    token = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirmation = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirmation']:
            raise serializers.ValidationError({
                'password_confirmation': "Password fields don't match."
            })
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification."""
    token = serializers.CharField(required=True)


# ========================
# TEAM SERIALIZERS
# ========================

class CRMTeamSerializer(serializers.ModelSerializer):
    """Serializer for CRM teams."""
    owner = UserSerializer(source='user', read_only=True)
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = CRMTeam
        fields = [
            'id', 'name', 'owner', 'members_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def get_members_count(self, obj):
        return obj.members.count()


class CRMTeamCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating CRM teams."""
    class Meta:
        model = CRMTeam
        fields = ['name']

    def create(self, validated_data):
        user = self.context['request'].user
        team = CRMTeam.objects.create(user=user, **validated_data)
        
        # Add owner as team member
        CRMTeamUser.objects.create(crm_team=team, user=user)
        
        # Set as current team if user has no current team
        if not user.current_crm_team:
            user.current_crm_team = team
            user.save(update_fields=['current_crm_team'])
        
        return team


class CRMTeamMemberSerializer(serializers.ModelSerializer):
    """Serializer for CRM team members."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = CRMTeamUser
        fields = ['id', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class CRMTeamInvitationSerializer(serializers.ModelSerializer):
    """Serializer for team invitations."""
    class Meta:
        model = CRMTeamInvitation
        fields = ['id', 'email', 'created_at']
        read_only_fields = ['id', 'created_at']


class TeamInviteSerializer(serializers.Serializer):
    """Serializer for inviting users to a team."""
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        team = self.context.get('team')
        
        # Check if already a member
        if CRMTeamUser.objects.filter(
            crm_team=team,
            user__email=value
        ).exists():
            raise serializers.ValidationError('User is already a team member.')
        
        # Check if invitation already exists
        if CRMTeamInvitation.objects.filter(
            crm_team=team,
            email=value
        ).exists():
            raise serializers.ValidationError('Invitation already sent to this email.')
        
        return value


class SwitchTeamSerializer(serializers.Serializer):
    """Serializer for switching current team."""
    team_id = serializers.IntegerField(required=True)

    def validate_team_id(self, value):
        user = self.context['request'].user
        
        # Check if user is member of the team
        if not CRMTeamUser.objects.filter(
            crm_team_id=value,
            user=user
        ).exists():
            raise serializers.ValidationError('You are not a member of this team.')
        
        return value


# ========================
# DEVICE/LOGIN SERIALIZERS
# ========================

class DeviceSerializer(serializers.ModelSerializer):
    """Serializer for user devices."""
    class Meta:
        model = Device
        fields = [
            'id', 'platform', 'platform_version', 'browser', 'browser_version',
            'is_desktop', 'is_mobile', 'language', 'is_trusted', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class LoginHistorySerializer(serializers.ModelSerializer):
    """Serializer for login history."""
    device = DeviceSerializer(read_only=True)

    class Meta:
        model = Login
        fields = ['id', 'ip_address', 'type', 'device', 'created_at']
        read_only_fields = ['id', 'created_at']


# ========================
# ROLE/PERMISSION SERIALIZERS
# ========================

class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for permissions."""
    class Meta:
        model = Permission
        fields = ['id', 'name', 'guard_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for roles."""
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Role
        fields = ['id', 'name', 'guard_name', 'permissions', 'permission_ids', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        permission_ids = validated_data.pop('permission_ids', [])
        role = Role.objects.create(**validated_data)
        
        if permission_ids:
            from .models import RoleHasPermission
            for perm_id in permission_ids:
                RoleHasPermission.objects.create(role=role, permission_id=perm_id)
        
        return role

    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if permission_ids is not None:
            from .models import RoleHasPermission
            RoleHasPermission.objects.filter(role=instance).delete()
            for perm_id in permission_ids:
                RoleHasPermission.objects.create(role=instance, permission_id=perm_id)
        
        return instance


class AssignRoleSerializer(serializers.Serializer):
    """Serializer for assigning roles to users."""
    role_id = serializers.IntegerField(required=True)

    def validate_role_id(self, value):
        if not Role.objects.filter(id=value).exists():
            raise serializers.ValidationError('Role not found.')
        return value

