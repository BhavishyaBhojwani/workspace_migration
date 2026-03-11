"""
URL patterns for Leads app.
Replicates Laravel's Lead routes structure.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LeadViewSet, LeadStatusViewSet, LeadSourceViewSet
from .test_views import test_create_lead

# Router for viewsets
router = DefaultRouter()
router.register(r'leads', LeadViewSet, basename='leads')
router.register(r'lead-statuses', LeadStatusViewSet, basename='lead-statuses')
router.register(r'lead-sources', LeadSourceViewSet, basename='lead-sources')

# Test URLs
urlpatterns = [
    # Test endpoint without authentication
    path('test-create-lead/', test_create_lead, name='test-create-lead'),
    
    # Include router URLs
    path('', include(router.urls)),
]
