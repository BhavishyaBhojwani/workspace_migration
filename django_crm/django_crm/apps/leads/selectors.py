from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from apps.crm.models import Person, Organisation
from apps.crm.serializers import UserMiniSerializer


class LeadSelector:
    """Selector class for Lead queries."""
    
    @staticmethod
    def get_queryset(user, include_converted=False):
        """Get base queryset for leads based on user permissions."""
        queryset = Lead.objects.filter(is_deleted=False)
        
        # Apply team filtering if user has team access
        if user and hasattr(user, 'current_crm_team_id') and user.current_crm_team_id:
            queryset = queryset.filter(team_id=user.current_crm_team_id)
        
        # Filter out converted leads unless explicitly requested
        if not include_converted:
            queryset = queryset.filter(converted_at__isnull=True)
        
        return queryset
    
    @staticmethod
    def filter_queryset(queryset, params):
        """Apply filters to queryset."""
        # Status filter
        status_id = params.get('status_id')
        if status_id:
            queryset = queryset.filter(lead_status_id=status_id)
        
        # Source filter
        source_id = params.get('source_id')
        if source_id:
            queryset = queryset.filter(lead_source_id=source_id)
        
        # Owner filter
        owner_id = params.get('owner_id')
        if owner_id:
            queryset = queryset.filter(user_owner_id=owner_id)
        
        # Assigned filter
        assigned_id = params.get('assigned_id')
        if assigned_id:
            queryset = queryset.filter(user_assigned_id=assigned_id)
        
        # Person filter
        person_id = params.get('person_id')
        if person_id:
            queryset = queryset.filter(person_id=person_id)
        
        # Organisation filter
        organisation_id = params.get('organisation_id')
        if organisation_id:
            queryset = queryset.filter(organisation_id=organisation_id)
        
        # Qualified filter
        qualified = params.get('qualified')
        if qualified is not None:
            queryset = queryset.filter(qualified=qualified.lower() == 'true')
        
        # Date range filter
        date_from = params.get('date_from')
        date_to = params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        # Amount range filter
        amount_min = params.get('amount_min')
        amount_max = params.get('amount_max')
        if amount_min:
            queryset = queryset.filter(amount__gte=amount_min)
        if amount_max:
            queryset = queryset.filter(amount__lte=amount_max)
        
        return queryset
    
    @staticmethod
    def search_queryset(queryset, search_term):
        """Apply search to queryset."""
        if not search_term:
            return queryset
        
        return queryset.filter(
            Q(title__icontains=search_term) |
            Q(description__icontains=search_term) |
            Q(person_id__in=Person.objects.filter(
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term)
            ).values_list('id', flat=True)) |
            Q(organisation_id__in=Organisation.objects.filter(
                name__icontains=search_term
            ).values_list('id', flat=True))
        )
    
    @staticmethod
    def sort_queryset(queryset, sort_field='created_at', direction='desc'):
        """Apply sorting to queryset."""
        valid_sort_fields = [
            'title', 'amount', 'created_at', 'updated_at', 'expected_close',
            'lead_status_id', 'lead_source_id', 'user_owner_id', 'user_assigned_id'
        ]
        
        if sort_field not in valid_sort_fields:
            sort_field = 'created_at'
        
        if direction.lower() == 'desc':
            sort_field = f'-{sort_field}'
        
        return queryset.order_by(sort_field)
    
    @staticmethod
    def with_relations(queryset):
        """Eager load related objects."""
        # Note: person_id, organisation_id, etc. are just ID fields, not actual FK relationships
        # So we don't use select_related for them
        return queryset


# Import at the end to avoid circular imports
from .models import Lead
