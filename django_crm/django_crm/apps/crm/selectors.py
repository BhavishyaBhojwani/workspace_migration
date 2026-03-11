"""
Selectors for CRM models - query logic separated from views.
Replicates Laravel's Scopes and Repository patterns.
"""
from django.db.models import Q, Prefetch
from django.contrib.contenttypes.models import ContentType

from .models import (
    Organisation, Person, Email, Phone, Address, Label, Labelable,
    OrganisationType, Industry, Timezone
)


class OrganisationSelector:
    """
    Query selectors for organisations.
    Replicates Laravel's BelongsToTeams scope and SearchFilters trait.
    """
    
    @staticmethod
    def get_queryset(user, include_deleted=False):
        """
        Get base queryset filtered by team.
        Replicates Laravel's BelongsToTeamsScope.
        """
        qs = Organisation.objects.all()
        
        # Team scoping - replicate Laravel's BelongsToTeamsScope
        if user.current_crm_team:
            qs = qs.filter(team_id=user.current_crm_team.id)
        
        # Soft delete filter
        if not include_deleted:
            qs = qs.filter(is_deleted=False)
        
        return qs
    
    @staticmethod
    def with_relations(queryset):
        """
        Eager load related data.
        Replicates Laravel's with() eager loading.
        """
        return queryset.prefetch_related(
            'emails',
            'phones',
            'addresses',
            'labelables__label',
            'people',
        ).select_related(
            'organisation_type',
            'industry',
            'timezone',
            'user_owner',
            'user_created',
        )
    
    @staticmethod
    def filter_queryset(queryset, params):
        """
        Apply filters to queryset.
        Replicates Laravel's SearchFilters::scopeFilter().
        """
        # Filter by user_owner_id
        if 'user_owner_id' in params:
            owner_ids = params.getlist('user_owner_id') if hasattr(params, 'getlist') else [params['user_owner_id']]
            if owner_ids:
                q = Q()
                for owner_id in owner_ids:
                    if owner_id == '0' or owner_id == 0:
                        q |= Q(user_owner_id__isnull=True)
                    else:
                        q |= Q(user_owner_id=owner_id)
                queryset = queryset.filter(q)
        
        # Filter by organisation_type_id
        if 'organisation_type_id' in params:
            type_ids = params.getlist('organisation_type_id') if hasattr(params, 'getlist') else [params['organisation_type_id']]
            if type_ids:
                queryset = queryset.filter(organisation_type_id__in=type_ids)
        
        # Filter by industry_id
        if 'industry_id' in params:
            industry_ids = params.getlist('industry_id') if hasattr(params, 'getlist') else [params['industry_id']]
            if industry_ids:
                queryset = queryset.filter(industry_id__in=industry_ids)
        
        # Filter by label_id (through labelables)
        if 'label_id' in params:
            label_ids = params.getlist('label_id') if hasattr(params, 'getlist') else [params['label_id']]
            if label_ids:
                content_type = ContentType.objects.get_for_model(Organisation)
                org_ids = Labelable.objects.filter(
                    labelable_type=content_type,
                    label_id__in=label_ids
                ).values_list('labelable_id', flat=True)
                
                q = Q(id__in=org_ids)
                if '0' in label_ids or 0 in label_ids:
                    # Include orgs without labels
                    labeled_ids = Labelable.objects.filter(
                        labelable_type=content_type
                    ).values_list('labelable_id', flat=True)
                    q |= ~Q(id__in=labeled_ids)
                queryset = queryset.filter(q)
        
        return queryset
    
    @staticmethod
    def search_queryset(queryset, search_term):
        """
        Apply search filter.
        Replicates Laravel's getSearchable() method.
        """
        if not search_term:
            return queryset
        
        search_term = search_term.lower().strip()
        return queryset.filter(
            Q(name__icontains=search_term) |
            Q(description__icontains=search_term) |
            Q(vat_number__icontains=search_term)
        )
    
    @staticmethod
    def sort_queryset(queryset, sort_field='created_at', sort_direction='desc'):
        """
        Apply sorting.
        Replicates Laravel's Sortable trait.
        """
        valid_fields = ['id', 'name', 'created_at', 'updated_at']
        
        if sort_field not in valid_fields:
            sort_field = 'created_at'
        
        if sort_direction == 'asc':
            return queryset.order_by(sort_field)
        return queryset.order_by(f'-{sort_field}')
    
    @staticmethod
    def get_by_id(user, organisation_id):
        """Get single organisation by ID with team scoping."""
        return OrganisationSelector.with_relations(
            OrganisationSelector.get_queryset(user)
        ).filter(id=organisation_id).first()
    
    @staticmethod
    def get_by_external_id(user, external_id):
        """Get single organisation by external_id with team scoping."""
        return OrganisationSelector.with_relations(
            OrganisationSelector.get_queryset(user)
        ).filter(external_id=external_id).first()


class PersonSelector:
    """
    Query selectors for persons.
    Replicates Laravel's BelongsToTeams scope and SearchFilters trait.
    """
    
    @staticmethod
    def get_queryset(user, include_deleted=False):
        """Get base queryset filtered by team."""
        qs = Person.objects.all()
        
        if user.current_crm_team:
            qs = qs.filter(team_id=user.current_crm_team.id)
        
        if not include_deleted:
            qs = qs.filter(is_deleted=False)
        
        return qs
    
    @staticmethod
    def with_relations(queryset):
        """Eager load related data."""
        return queryset.prefetch_related(
            'emails',
            'phones',
            'addresses',
            'labelables__label',
        ).select_related(
            'organisation',
            'user_owner',
            'user_created',
        )
    
    @staticmethod
    def filter_queryset(queryset, params):
        """
        Apply filters to queryset.
        Replicates Laravel's SearchFilters::scopeFilter().
        Filterable fields: ['user_owner_id', 'labels.id']
        """
        # Filter by user_owner_id
        if 'user_owner_id' in params:
            owner_ids = params.getlist('user_owner_id') if hasattr(params, 'getlist') else [params['user_owner_id']]
            if owner_ids:
                q = Q()
                for owner_id in owner_ids:
                    if owner_id == '0' or owner_id == 0:
                        q |= Q(user_owner_id__isnull=True)
                    else:
                        q |= Q(user_owner_id=owner_id)
                queryset = queryset.filter(q)
        
        # Filter by organisation_id
        if 'organisation_id' in params:
            org_ids = params.getlist('organisation_id') if hasattr(params, 'getlist') else [params['organisation_id']]
            if org_ids:
                queryset = queryset.filter(organisation_id__in=org_ids)
        
        # Filter by label_id (through labelables)
        if 'label_id' in params:
            label_ids = params.getlist('label_id') if hasattr(params, 'getlist') else [params['label_id']]
            if label_ids:
                content_type = ContentType.objects.get_for_model(Person)
                person_ids = Labelable.objects.filter(
                    labelable_type=content_type,
                    label_id__in=label_ids
                ).values_list('labelable_id', flat=True)
                
                q = Q(id__in=person_ids)
                if '0' in label_ids or 0 in label_ids:
                    # Include persons without labels
                    labeled_ids = Labelable.objects.filter(
                        labelable_type=content_type
                    ).values_list('labelable_id', flat=True)
                    q |= ~Q(id__in=labeled_ids)
                queryset = queryset.filter(q)
        
        return queryset
    
    @staticmethod
    def search_queryset(queryset, search_term):
        """Apply search filter."""
        if not search_term:
            return queryset
        
        search_term = search_term.lower().strip()
        return queryset.filter(
            Q(first_name__icontains=search_term) |
            Q(last_name__icontains=search_term) |
            Q(middle_name__icontains=search_term) |
            Q(description__icontains=search_term)
        )
    
    @staticmethod
    def sort_queryset(queryset, sort_field='created_at', sort_direction='desc'):
        """Apply sorting."""
        valid_fields = ['id', 'first_name', 'last_name', 'created_at', 'updated_at']
        
        if sort_field not in valid_fields:
            sort_field = 'created_at'
        
        if sort_direction == 'asc':
            return queryset.order_by(sort_field)
        return queryset.order_by(f'-{sort_field}')


class LabelSelector:
    """Query selectors for labels."""
    
    @staticmethod
    def get_queryset(user):
        """Get labels for user's team."""
        qs = Label.objects.filter(is_deleted=False)
        
        if user.current_crm_team:
            qs = qs.filter(team_id=user.current_crm_team.id)
        
        return qs


class OrganisationTypeSelector:
    """Query selectors for organisation types."""
    
    @staticmethod
    def get_queryset(user):
        """Get organisation types with team scoping + global."""
        qs = OrganisationType.objects.filter(is_deleted=False)
        
        if user.current_crm_team:
            qs = qs.filter(
                Q(team_id=user.current_crm_team.id) |
                Q(team_id__isnull=True)
            )
        
        return qs


class IndustrySelector:
    """Query selectors for industries."""
    
    @staticmethod
    def get_queryset(user):
        """Get industries with team scoping + global."""
        qs = Industry.objects.filter(is_deleted=False)
        
        if user.current_crm_team:
            qs = qs.filter(
                Q(team_id=user.current_crm_team.id) |
                Q(team_id__isnull=True)
            )
        
        return qs

# ============================================================================
# LEAD, PIPELINE & DEAL SELECTORS
# ============================================================================

from apps.pipeline.models import (
    LeadStatus, LeadSource, Pipeline, PipelineStage,
    PipelineStageProbability, Lead, Deal, DealProduct
)


class PipelineSelector:
    """Query selectors for pipelines."""
    
    @staticmethod
    def get_queryset(user, include_deleted=False):
        """Get base queryset filtered by team."""
        qs = Pipeline.objects.all()
        
        if user.current_crm_team:
            qs = qs.filter(
                Q(team_id=user.current_crm_team.id) |
                Q(team_id__isnull=True)
            )
        
        if not include_deleted:
            qs = qs.filter(is_deleted=False)
        
        return qs
    
    @staticmethod
    def with_stages(queryset):
        """Eager load pipeline stages."""
        return queryset.prefetch_related(
            Prefetch(
                'stages',
                queryset=PipelineStage.objects.filter(is_deleted=False).order_by('order')
            )
        )
    
    @staticmethod
    def get_by_model(user, model_type, include_deleted=False):
        """Get pipelines filtered by model type (Lead, Deal, Quote)."""
        qs = PipelineSelector.get_queryset(user, include_deleted)
        return qs.filter(model=model_type)
    
    @staticmethod
    def get_default_for_model(user, model_type):
        """Get default pipeline for a model type."""
        return PipelineSelector.get_by_model(user, model_type).first()


class PipelineStageSelector:
    """Query selectors for pipeline stages."""
    
    @staticmethod
    def get_queryset(user, include_deleted=False):
        """Get base queryset filtered by team."""
        qs = PipelineStage.objects.all()
        
        if user.current_crm_team:
            qs = qs.filter(
                Q(team_id=user.current_crm_team.id) |
                Q(team_id__isnull=True)
            )
        
        if not include_deleted:
            qs = qs.filter(is_deleted=False)
        
        return qs.order_by('pipeline_id', 'order')
    
    @staticmethod
    def get_for_pipeline(pipeline_id, include_deleted=False):
        """Get stages for a specific pipeline."""
        qs = PipelineStage.objects.filter(pipeline_id=pipeline_id)
        
        if not include_deleted:
            qs = qs.filter(is_deleted=False)
        
        return qs.order_by('order')


class LeadStatusSelector:
    """Query selectors for lead statuses."""
    
    @staticmethod
    def get_queryset(user, include_deleted=False):
        """Get lead statuses with team scoping."""
        qs = LeadStatus.objects.all()
        
        if user.current_crm_team:
            qs = qs.filter(
                Q(team_id=user.current_crm_team.id) |
                Q(team_id__isnull=True)
            )
        
        if not include_deleted:
            qs = qs.filter(is_deleted=False)
        
        return qs.order_by('order', 'name')


class LeadSourceSelector:
    """Query selectors for lead sources."""
    
    @staticmethod
    def get_queryset(user, include_deleted=False):
        """Get lead sources with team scoping."""
        qs = LeadSource.objects.all()
        
        if user.current_crm_team:
            qs = qs.filter(
                Q(team_id=user.current_crm_team.id) |
                Q(team_id__isnull=True)
            )
        
        if not include_deleted:
            qs = qs.filter(is_deleted=False)
        
        return qs.order_by('name')


class LeadSelector:
    """
    Query selectors for leads.
    Replicates Laravel's BelongsToTeams scope and SearchFilters trait.
    """
    
    @staticmethod
    def get_queryset(user, include_deleted=False, include_converted=False):
        """Get base queryset filtered by team."""
        qs = Lead.objects.all()
        
        if user.current_crm_team:
            qs = qs.filter(team_id=user.current_crm_team.id)
        
        if not include_deleted:
            qs = qs.filter(is_deleted=False)
        
        if not include_converted:
            qs = qs.filter(converted_at__isnull=True)
        
        return qs
    
    @staticmethod
    def with_relations(queryset):
        """Eager load related data."""
        return queryset.select_related(
            'person',
            'organisation',
            'lead_status',
            'lead_source',
            'pipeline',
            'pipeline_stage',
            'pipeline_stage__pipeline_stage_probability',
            'user_owner',
            'user_assigned',
        ).prefetch_related(
            'person__emails',
            'person__phones',
            'labelables__label',
        )
    
    @staticmethod
    def filter_queryset(queryset, params):
        """Apply filters to queryset."""
        # Filter by lead_status_id
        if 'lead_status_id' in params:
            status_ids = params.getlist('lead_status_id') if hasattr(params, 'getlist') else [params['lead_status_id']]
            if status_ids:
                queryset = queryset.filter(lead_status_id__in=status_ids)
        
        # Filter by lead_source_id
        if 'lead_source_id' in params:
            source_ids = params.getlist('lead_source_id') if hasattr(params, 'getlist') else [params['lead_source_id']]
            if source_ids:
                queryset = queryset.filter(lead_source_id__in=source_ids)
        
        # Filter by pipeline_id
        if 'pipeline_id' in params:
            pipeline_ids = params.getlist('pipeline_id') if hasattr(params, 'getlist') else [params['pipeline_id']]
            if pipeline_ids:
                queryset = queryset.filter(pipeline_id__in=pipeline_ids)
        
        # Filter by pipeline_stage_id
        if 'pipeline_stage_id' in params:
            stage_ids = params.getlist('pipeline_stage_id') if hasattr(params, 'getlist') else [params['pipeline_stage_id']]
            if stage_ids:
                queryset = queryset.filter(pipeline_stage_id__in=stage_ids)
        
        # Filter by person_id
        if 'person_id' in params:
            queryset = queryset.filter(person_id=params['person_id'])
        
        # Filter by organisation_id
        if 'organisation_id' in params:
            queryset = queryset.filter(organisation_id=params['organisation_id'])
        
        # Filter by user_owner_id
        if 'user_owner_id' in params:
            owner_ids = params.getlist('user_owner_id') if hasattr(params, 'getlist') else [params['user_owner_id']]
            if owner_ids:
                q = Q()
                for owner_id in owner_ids:
                    if owner_id == '0' or owner_id == 0:
                        q |= Q(user_owner_id__isnull=True)
                    else:
                        q |= Q(user_owner_id=owner_id)
                queryset = queryset.filter(q)
        
        # Filter by user_assigned_id
        if 'user_assigned_id' in params:
            assigned_ids = params.getlist('user_assigned_id') if hasattr(params, 'getlist') else [params['user_assigned_id']]
            if assigned_ids:
                queryset = queryset.filter(user_assigned_id__in=assigned_ids)
        
        # Filter by qualified
        if 'qualified' in params:
            queryset = queryset.filter(qualified=params['qualified'])
        
        return queryset
    
    @staticmethod
    def search_queryset(queryset, search_term):
        """Search leads by title, description, person name, or organisation."""
        if not search_term:
            return queryset
        
        return queryset.filter(
            Q(title__icontains=search_term) |
            Q(description__icontains=search_term) |
            Q(lead_id__icontains=search_term) |
            Q(person__first_name__icontains=search_term) |
            Q(person__last_name__icontains=search_term) |
            Q(organisation__name__icontains=search_term)
        )
    
    @staticmethod
    def sort_queryset(queryset, sort_field, sort_order='asc'):
        """Apply sorting to queryset."""
        if not sort_field:
            return queryset.order_by('-created_at')
        
        prefix = '-' if sort_order == 'desc' else ''
        
        sort_mapping = {
            'title': 'title',
            'amount': 'amount',
            'status': 'lead_status__order',
            'stage': 'pipeline_stage__order',
            'created_at': 'created_at',
            'expected_close': 'expected_close',
        }
        
        db_field = sort_mapping.get(sort_field, sort_field)
        return queryset.order_by(f'{prefix}{db_field}')


class DealSelector:
    """
    Query selectors for deals.
    Replicates Laravel's BelongsToTeams scope and SearchFilters trait.
    """
    
    @staticmethod
    def get_queryset(user, include_deleted=False, include_closed=True):
        """Get base queryset filtered by team."""
        qs = Deal.objects.all()
        
        if hasattr(user, 'current_crm_team') and user.current_crm_team:
            qs = qs.filter(team_id=user.current_crm_team.id)
        
        if not include_deleted:
            qs = qs.filter(is_deleted=False)
        
        if not include_closed:
            qs = qs.filter(closed_status__isnull=True)
        
        return qs
    
    @staticmethod
    def with_relations(queryset):
        """Eager load related data."""
        # Simplified to avoid prefetching non-existent relationships
        return queryset.select_related(
            'person',
            'organisation', 
            'pipeline',
            'pipeline_stage',
            'user_owner',
            'user_assigned',
        )
    
    @staticmethod
    def filter_queryset(queryset, params):
        """Apply filters to queryset."""
        # Filter by closed_status
        if 'closed_status' in params:
            status = params['closed_status']
            if status == 'open':
                queryset = queryset.filter(closed_status__isnull=True)
            elif status in ['won', 'lost']:
                queryset = queryset.filter(closed_status=status)
        
        # Filter by pipeline_id
        if 'pipeline_id' in params:
            pipeline_ids = params.getlist('pipeline_id') if hasattr(params, 'getlist') else [params['pipeline_id']]
            if pipeline_ids:
                queryset = queryset.filter(pipeline_id__in=pipeline_ids)
        
        # Filter by pipeline_stage_id
        if 'pipeline_stage_id' in params:
            stage_ids = params.getlist('pipeline_stage_id') if hasattr(params, 'getlist') else [params['pipeline_stage_id']]
            if stage_ids:
                queryset = queryset.filter(pipeline_stage_id__in=stage_ids)
        
        # Filter by person_id
        if 'person_id' in params:
            queryset = queryset.filter(person_id=params['person_id'])
        
        # Filter by organisation_id
        if 'organisation_id' in params:
            queryset = queryset.filter(organisation_id=params['organisation_id'])
        
        # Filter by user_owner_id
        if 'user_owner_id' in params:
            owner_ids = params.getlist('user_owner_id') if hasattr(params, 'getlist') else [params['user_owner_id']]
            if owner_ids:
                q = Q()
                for owner_id in owner_ids:
                    if owner_id == '0' or owner_id == 0:
                        q |= Q(user_owner_id__isnull=True)
                    else:
                        q |= Q(user_owner_id=owner_id)
                queryset = queryset.filter(q)
        
        # Filter by user_assigned_id
        if 'user_assigned_id' in params:
            assigned_ids = params.getlist('user_assigned_id') if hasattr(params, 'getlist') else [params['user_assigned_id']]
            if assigned_ids:
                queryset = queryset.filter(user_assigned_id__in=assigned_ids)
        
        # Filter by amount range
        if 'amount_min' in params:
            amount_min = int(float(params['amount_min']) * 100)
            queryset = queryset.filter(amount__gte=amount_min)
        
        if 'amount_max' in params:
            amount_max = int(float(params['amount_max']) * 100)
            queryset = queryset.filter(amount__lte=amount_max)
        
        return queryset
    
    @staticmethod
    def search_queryset(queryset, search_term):
        """Search deals by title, description, person name, or organisation."""
        if not search_term:
            return queryset
        
        return queryset.filter(
            Q(title__icontains=search_term) |
            Q(description__icontains=search_term) |
            Q(deal_id__icontains=search_term) |
            Q(person__first_name__icontains=search_term) |
            Q(person__last_name__icontains=search_term) |
            Q(organisation__name__icontains=search_term)
        )
    
    @staticmethod
    def sort_queryset(queryset, sort_field, sort_order='asc'):
        """Apply sorting to queryset."""
        if not sort_field:
            return queryset.order_by('-created_at')
        
        prefix = '-' if sort_order == 'desc' else ''
        
        sort_mapping = {
            'title': 'title',
            'amount': 'amount',
            'stage': 'pipeline_stage__order',
            'created_at': 'created_at',
            'expected_close': 'expected_close',
            'closed_at': 'closed_at',
        }
        
        db_field = sort_mapping.get(sort_field, sort_field)
        return queryset.order_by(f'{prefix}{db_field}')
    
    @staticmethod
    def get_open_deals(user):
        """Get open deals (not won/lost)."""
        return DealSelector.get_queryset(user, include_closed=False)
    
    @staticmethod
    def get_won_deals(user, include_deleted=False):
        """Get won deals."""
        qs = DealSelector.get_queryset(user, include_deleted=include_deleted)
        return qs.filter(closed_status='won')
    
    @staticmethod
    def get_lost_deals(user, include_deleted=False):
        """Get lost deals."""
        qs = DealSelector.get_queryset(user, include_deleted=include_deleted)
        return qs.filter(closed_status='lost')