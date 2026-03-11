from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# Register leads app ViewSets
from apps.leads.views import LeadViewSet, LeadStatusViewSet, LeadSourceViewSet
router.register(r'leads', LeadViewSet, basename='leads')
router.register(r'lead-statuses', LeadStatusViewSet, basename='lead-statuses')
router.register(r'lead-sources', LeadSourceViewSet, basename='lead-sources')

# Register CRM app ViewSets
from apps.crm.views import DealViewSet
router.register(r'deals', DealViewSet, basename='deals')
