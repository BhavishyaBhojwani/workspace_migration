"""
Authentication and Account Views.
Implements JWT authentication similar to Laravel Breeze + Sanctum.
"""
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError

from .models import (
    CRMTeam, CRMTeamUser, CRMTeamInvitation, Device, Login,
    Role, Permission, ModelHasRole
)
from .serializers import (
    UserSerializer, UserUpdateSerializer, RegisterSerializer,
    LoginSerializer as AuthLoginSerializer, CustomTokenObtainPairSerializer,
    PasswordChangeSerializer, PasswordResetRequestSerializer, PasswordResetSerializer,
    CRMTeamSerializer, CRMTeamCreateSerializer, CRMTeamMemberSerializer,
    CRMTeamInvitationSerializer, TeamInviteSerializer, SwitchTeamSerializer,
    DeviceSerializer, LoginHistorySerializer, RoleSerializer, PermissionSerializer,
    AssignRoleSerializer
)
from .permissions import IsTeamOwner, IsTeamMember, HasPermission


User = get_user_model()


# ========================
# AUTHENTICATION VIEWS
# ========================

class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.
    POST /api/v1/auth/register
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'Registration successful',
            'data': {
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    User login endpoint.
    POST /api/v1/auth/login
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AuthLoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        remember = serializer.validated_data.get('remember', False)
        
        # Update last online
        user.last_online_at = timezone.now()
        user.save(update_fields=['last_online_at'])
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        # Add custom claims
        refresh['name'] = user.name
        refresh['email'] = user.email
        refresh['crm_access'] = user.crm_access
        if user.current_crm_team:
            refresh['current_team_id'] = user.current_crm_team.id
        
        # Track login
        self._track_login(request, user)
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }
        })

    def _track_login(self, request, user):
        """Track user login with device info."""
        try:
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Create or get device
            device, _ = Device.objects.get_or_create(
                user=user,
                browser=self._parse_browser(user_agent),
                platform=self._parse_platform(user_agent),
                defaults={
                    'is_desktop': 'Mobile' not in user_agent,
                    'is_mobile': 'Mobile' in user_agent,
                }
            )
            
            # Create login record
            Login.objects.create(
                user=user,
                device=device,
                ip_address=ip_address,
                type=Login.TYPE_LOGIN
            )
        except Exception:
            pass  # Don't fail login if tracking fails

    def _get_client_ip(self, request):
        """Get client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '127.0.0.1')

    def _parse_browser(self, user_agent):
        """Parse browser from user agent."""
        if 'Chrome' in user_agent:
            return 'Chrome'
        elif 'Firefox' in user_agent:
            return 'Firefox'
        elif 'Safari' in user_agent:
            return 'Safari'
        elif 'Edge' in user_agent:
            return 'Edge'
        return 'Unknown'

    def _parse_platform(self, user_agent):
        """Parse platform from user agent."""
        if 'Windows' in user_agent:
            return 'Windows'
        elif 'Mac' in user_agent:
            return 'macOS'
        elif 'Linux' in user_agent:
            return 'Linux'
        elif 'Android' in user_agent:
            return 'Android'
        elif 'iPhone' in user_agent or 'iPad' in user_agent:
            return 'iOS'
        return 'Unknown'


class LogoutView(APIView):
    """
    User logout endpoint. Blacklists the refresh token.
    POST /api/v1/auth/logout
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Track logout
            self._track_logout(request)
            
            return Response({
                'success': True,
                'message': 'Logout successful'
            })
        except TokenError:
            return Response({
                'success': False,
                'message': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)

    def _track_logout(self, request):
        """Track user logout."""
        try:
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
            if not ip_address:
                ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')
            
            Login.objects.create(
                user=request.user,
                ip_address=ip_address,
                type=Login.TYPE_LOGOUT
            )
        except Exception:
            pass


class RefreshTokenView(TokenRefreshView):
    """
    Token refresh endpoint.
    POST /api/v1/auth/refresh
    """
    pass


class CurrentUserView(APIView):
    """
    Get current authenticated user.
    GET /api/v1/auth/user
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'success': True,
            'data': UserSerializer(request.user).data
        })


class UpdateProfileView(generics.UpdateAPIView):
    """
    Update current user profile.
    PUT/PATCH /api/v1/auth/profile
    """
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'data': UserSerializer(instance).data
        })


class ChangePasswordView(APIView):
    """
    Change current user password.
    POST /api/v1/auth/password
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        
        return Response({
            'success': True,
            'message': 'Password changed successfully'
        })


class ForgotPasswordView(APIView):
    """
    Request password reset email.
    POST /api/v1/auth/forgot-password
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # TODO: Send password reset email
        # email = serializer.validated_data['email']
        # user = User.objects.filter(email=email).first()
        # if user:
        #     send_password_reset_email(user)
        
        return Response({
            'success': True,
            'message': 'If the email exists, a reset link has been sent.'
        })


class ResetPasswordView(APIView):
    """
    Reset password with token.
    POST /api/v1/auth/reset-password
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # TODO: Validate token and reset password
        # token = serializer.validated_data['token']
        # email = serializer.validated_data['email']
        # password = serializer.validated_data['password']
        
        return Response({
            'success': True,
            'message': 'Password has been reset.'
        })


class VerifyEmailView(APIView):
    """
    Verify email with token.
    POST /api/v1/auth/verify-email
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # TODO: Implement email verification
        return Response({
            'success': True,
            'message': 'Email verified successfully.'
        })


# ========================
# TEAM VIEWS
# ========================

class TeamViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRM team management.
    Implements team-based access control similar to Laravel's multi-team structure.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return teams the user is a member of."""
        return CRMTeam.objects.filter(
            members__user=self.request.user,
            is_deleted=False
        ).distinct()

    def get_serializer_class(self):
        if self.action == 'create':
            return CRMTeamCreateSerializer
        return CRMTeamSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        team = serializer.save()
        
        return Response({
            'success': True,
            'message': 'Team created successfully',
            'data': CRMTeamSerializer(team).data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Only owner can update
        if instance.user != request.user:
            return Response({
                'success': False,
                'message': 'Only team owner can update the team.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'success': True,
            'message': 'Team updated successfully',
            'data': CRMTeamSerializer(instance).data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Only owner can delete
        if instance.user != request.user:
            return Response({
                'success': False,
                'message': 'Only team owner can delete the team.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Soft delete
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()
        
        return Response({
            'success': True,
            'message': 'Team deleted successfully'
        })

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get team members."""
        team = self.get_object()
        members = CRMTeamUser.objects.filter(crm_team=team).select_related('user')
        serializer = CRMTeamMemberSerializer(members, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        """Invite user to team."""
        team = self.get_object()
        
        # Only owner can invite
        if team.user != request.user:
            return Response({
                'success': False,
                'message': 'Only team owner can invite members.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = TeamInviteSerializer(
            data=request.data,
            context={'team': team}
        )
        serializer.is_valid(raise_exception=True)
        
        invitation = CRMTeamInvitation.objects.create(
            crm_team=team,
            email=serializer.validated_data['email']
        )
        
        # TODO: Send invitation email
        
        return Response({
            'success': True,
            'message': 'Invitation sent successfully',
            'data': CRMTeamInvitationSerializer(invitation).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='members/(?P<user_id>[^/.]+)')
    def remove_member(self, request, pk=None, user_id=None):
        """Remove member from team."""
        team = self.get_object()
        
        # Only owner can remove (except self)
        if team.user != request.user and str(request.user.id) != user_id:
            return Response({
                'success': False,
                'message': 'Only team owner can remove members.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Can't remove owner
        if str(team.user.id) == user_id:
            return Response({
                'success': False,
                'message': 'Cannot remove team owner.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        CRMTeamUser.objects.filter(crm_team=team, user_id=user_id).delete()
        
        return Response({
            'success': True,
            'message': 'Member removed successfully'
        })

    @action(detail=True, methods=['get'])
    def invitations(self, request, pk=None):
        """Get pending invitations."""
        team = self.get_object()
        invitations = CRMTeamInvitation.objects.filter(crm_team=team)
        serializer = CRMTeamInvitationSerializer(invitations, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })


class SwitchTeamView(APIView):
    """
    Switch current team.
    POST /api/v1/teams/switch
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SwitchTeamSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        team_id = serializer.validated_data['team_id']
        request.user.current_crm_team_id = team_id
        request.user.save(update_fields=['current_crm_team_id'])
        
        return Response({
            'success': True,
            'message': 'Team switched successfully',
            'data': {
                'current_team': CRMTeamSerializer(request.user.current_crm_team).data
            }
        })


class AcceptInvitationView(APIView):
    """
    Accept team invitation.
    POST /api/v1/teams/invitations/{id}/accept
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, invitation_id):
        try:
            invitation = CRMTeamInvitation.objects.get(
                id=invitation_id,
                email=request.user.email
            )
        except CRMTeamInvitation.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invitation not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Add user to team
        CRMTeamUser.objects.get_or_create(
            crm_team=invitation.crm_team,
            user=request.user
        )
        
        # Delete invitation
        invitation.delete()
        
        return Response({
            'success': True,
            'message': 'Invitation accepted',
            'data': {
                'team': CRMTeamSerializer(invitation.crm_team).data
            }
        })


# ========================
# USER MANAGEMENT VIEWS
# ========================

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user management.
    Admin-only endpoints.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = 'manage_users'

    def get_queryset(self):
        return User.objects.all()


# ========================
# ROLE/PERMISSION VIEWS
# ========================

class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for role management.
    """
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = 'manage_roles'

    def get_queryset(self):
        team = self.request.user.current_crm_team
        if team:
            return Role.objects.filter(team_id=team.id)
        return Role.objects.filter(team__isnull=True)


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing permissions.
    """
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    queryset = Permission.objects.all()


class AssignRoleView(APIView):
    """
    Assign role to user.
    POST /api/v1/users/{user_id}/roles
    """
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = 'manage_roles'

    def post(self, request, user_id):
        serializer = AssignRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(User)
        
        role_id = serializer.validated_data['role_id']
        ModelHasRole.objects.get_or_create(
            role_id=role_id,
            model_type=content_type.model,
            model_id=user.id,
            defaults={'team': request.user.current_crm_team}
        )
        
        return Response({
            'success': True,
            'message': 'Role assigned successfully'
        })

    def delete(self, request, user_id):
        """Remove role from user."""
        role_id = request.data.get('role_id')
        if not role_id:
            return Response({
                'success': False,
                'message': 'role_id is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(User)
        
        ModelHasRole.objects.filter(
            role_id=role_id,
            model_type=content_type.model,
            model_id=user_id
        ).delete()
        
        return Response({
            'success': True,
            'message': 'Role removed successfully'
        })


# ========================
# DEVICE/LOGIN VIEWS
# ========================

class DeviceListView(generics.ListAPIView):
    """
    List user's devices.
    GET /api/v1/auth/devices
    """
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Device.objects.filter(user=self.request.user)


class LoginHistoryView(generics.ListAPIView):
    """
    List user's login history.
    GET /api/v1/auth/logins
    """
    serializer_class = LoginHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Login.objects.filter(user=self.request.user).select_related('device')[:50]

