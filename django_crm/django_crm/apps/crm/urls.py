"""
CRM URL patterns.
Replicates Laravel's CRM routes structure.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    OrganisationViewSet, PersonViewSet,
    LabelViewSet, OrganisationTypeViewSet, IndustryViewSet,
    PipelineViewSet, PipelineStageViewSet,
    DealViewSet,
)
from apps.leads.views import LeadViewSet, LeadStatusViewSet, LeadSourceViewSet

# Router for viewsets
router = DefaultRouter()
router.register(r'organisations', OrganisationViewSet, basename='organisations')
router.register(r'people', PersonViewSet, basename='people')
router.register(r'labels', LabelViewSet, basename='labels')
router.register(r'organisation-types', OrganisationTypeViewSet, basename='organisation-types')
router.register(r'industries', IndustryViewSet, basename='industries')

# Lead, Pipeline & Deal routes
router.register(r'pipelines', PipelineViewSet, basename='pipelines')
router.register(r'pipeline-stages', PipelineStageViewSet, basename='pipeline-stages')
router.register(r'lead-statuses', LeadStatusViewSet, basename='lead-statuses')
router.register(r'lead-sources', LeadSourceViewSet, basename='lead-sources')
router.register(r'leads', LeadViewSet, basename='leads')
router.register(r'deals', DealViewSet, basename='deals')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('apps.leads.urls')),  # Include leads app URLs
]
