"""
API v1 URL Configuration.
"""
from django.urls import path, include
from .router import router

urlpatterns = [
    # Account & Authentication routes
    path("", include("apps.accounts.urls")),
    
    # CRM routes (organisations, people, etc.)
    path("", include("apps.crm.urls")),
    
    # ViewSet routes
    path("", include(router.urls)),
]
