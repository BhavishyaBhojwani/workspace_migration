"""
Authentication and Account URL patterns.
Replicates Laravel Breeze + Sanctum authentication routes.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    # Auth views
    RegisterView, LoginView, LogoutView, RefreshTokenView,
    CurrentUserView, UpdateProfileView, ChangePasswordView,
    ForgotPasswordView, ResetPasswordView, VerifyEmailView,
    DeviceListView, LoginHistoryView,
    # Team views
    TeamViewSet, SwitchTeamView, AcceptInvitationView,
    # User management
    UserViewSet,
    # Role/Permission views
    RoleViewSet, PermissionViewSet, AssignRoleView,
)

# Router for viewsets
router = DefaultRouter()
router.register(r'teams', TeamViewSet, basename='teams')
router.register(r'users', UserViewSet, basename='users')
router.register(r'roles', RoleViewSet, basename='roles')
router.register(r'permissions', PermissionViewSet, basename='permissions')

# Auth URL patterns (similar to Laravel Breeze)
auth_patterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('user/', CurrentUserView.as_view(), name='current_user'),
    path('profile/', UpdateProfileView.as_view(), name='update_profile'),
    path('password/', ChangePasswordView.as_view(), name='change_password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path('devices/', DeviceListView.as_view(), name='devices'),
    path('logins/', LoginHistoryView.as_view(), name='login_history'),
]

# Team URL patterns
team_patterns = [
    path('switch', SwitchTeamView.as_view(), name='switch_team'),
    path('invitations/<int:invitation_id>/accept', AcceptInvitationView.as_view(), name='accept_invitation'),
]

# User management patterns
user_patterns = [
    path('<int:user_id>/roles', AssignRoleView.as_view(), name='assign_role'),
]

urlpatterns = [
    path('auth/', include((auth_patterns, 'auth'))),
    path('teams/', include((team_patterns, 'team_actions'))),
    path('users/', include((user_patterns, 'user_actions'))),
    path('', include(router.urls)),
]

