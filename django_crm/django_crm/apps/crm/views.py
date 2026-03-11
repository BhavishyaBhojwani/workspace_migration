"""
CRM API Views.
Replicates Laravel's controller behavior endpoint-by-endpoint.
"""
from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from apps.accounts.permissions import HasPermission, IsCRMUser

from .models import Organisation, Person, Label, OrganisationType, Industry
from .selectors import (
    OrganisationSelector, PersonSelector, LabelSelector,
    OrganisationTypeSelector, IndustrySelector,
    PipelineSelector, PipelineStageSelector, DealSelector
)
from .services import (
    OrganisationService, PersonService,
    PipelineService, PipelineStageService, DealService
)
from .serializers import (
    OrganisationListSerializer, OrganisationDetailSerializer,
    OrganisationCreateSerializer, OrganisationUpdateSerializer,
    PersonListSerializer, PersonDetailSerializer,
    PersonCreateSerializer, PersonUpdateSerializer,
    LabelSerializer, OrganisationTypeSerializer, IndustrySerializer,
    PipelineSerializer, PipelineListSerializer, PipelineCreateSerializer,
    PipelineUpdateSerializer, PipelineStageSerializer, PipelineStageCreateSerializer,
    PipelineStageUpdateSerializer, DealSerializer, DealListSerializer, DealCreateSerializer,
    DealUpdateSerializer, DealCloseSerializer
)
from apps.pipeline.models import Lead, Deal, Pipeline, PipelineStage


class OrganisationViewSet(ViewSet):
    """
    ViewSet for organisations.
    Replicates Laravel's OrganisationController.
    
    Endpoints:
        GET  /organisations           - List organisations
        POST /organisations           - Create organisation  
        GET  /organisations/{id}      - Get organisation
        PUT  /organisations/{id}      - Update organisation
        DELETE /organisations/{id}    - Delete organisation
        GET  /organisations/search    - Search organisations
        GET  /organisations/{id}/autocomplete - Get autocomplete data
    """
    permission_classes = [IsAuthenticated, IsCRMUser]
    
    def list(self, request):
        """
        GET /organisations
        
        List organisations with pagination, filtering, sorting.
        Replicates Laravel's OrganisationController::index().
        """
        user = request.user
        
        # Get base queryset with team scoping
        queryset = OrganisationSelector.get_queryset(user)
        
        # Apply filters
        queryset = OrganisationSelector.filter_queryset(queryset, request.query_params)
        
        # Apply search
        search = request.query_params.get('search', '')
        if search:
            queryset = OrganisationSelector.search_queryset(queryset, search)
        
        # Apply sorting
        sort = request.query_params.get('sort', 'created_at')
        direction = request.query_params.get('direction', 'desc')
        queryset = OrganisationSelector.sort_queryset(queryset, sort, direction)
        
        # Eager load relations
        queryset = OrganisationSelector.with_relations(queryset)
        
        # Pagination - matches Laravel's paginate(30)
        page = request.query_params.get('page', 1)
        per_page = request.query_params.get('per_page', 30)
        
        try:
            per_page = int(per_page)
            page = int(page)
        except (ValueError, TypeError):
            per_page = 30
            page = 1
        
        # If total count is less than per_page, return all without pagination
        total_count = queryset.count()
        
        if total_count <= per_page:
            serializer = OrganisationListSerializer(queryset, many=True)
            return Response({
                'success': True,
                'data': serializer.data,
                'meta': {
                    'current_page': 1,
                    'last_page': 1,
                    'per_page': per_page,
                    'total': total_count,
                }
            })
        
        # Paginate results
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        serializer = OrganisationListSerializer(page_obj, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {
                'current_page': page_obj.number,
                'last_page': paginator.num_pages,
                'per_page': per_page,
                'total': paginator.count,
            },
            'links': {
                'first': self._build_page_link(request, 1),
                'last': self._build_page_link(request, paginator.num_pages),
                'prev': self._build_page_link(request, page_obj.number - 1) if page_obj.has_previous() else None,
                'next': self._build_page_link(request, page_obj.number + 1) if page_obj.has_next() else None,
            }
        })
    
    def create(self, request):
        """
        POST /organisations
        
        Create a new organisation.
        Replicates Laravel's OrganisationController::store().
        """
        serializer = OrganisationCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        organisation = OrganisationService.create(
            user=request.user,
            data=serializer.validated_data
        )
        
        # Refresh and eager load
        organisation = OrganisationSelector.get_by_id(request.user, organisation.id)
        
        return Response({
            'success': True,
            'message': 'Organization stored',
            'data': OrganisationDetailSerializer(organisation).data
        }, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None):
        """
        GET /organisations/{id}
        
        Get a single organisation.
        Replicates Laravel's OrganisationController::show().
        """
        organisation = OrganisationSelector.get_by_id(request.user, pk)
        
        if not organisation:
            return Response({
                'success': False,
                'message': 'Organization not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'data': OrganisationDetailSerializer(organisation).data
        })
    
    def update(self, request, pk=None):
        """
        PUT/PATCH /organisations/{id}
        
        Update an organisation.
        Replicates Laravel's OrganisationController::update().
        """
        organisation = OrganisationSelector.get_by_id(request.user, pk)
        
        if not organisation:
            return Response({
                'success': False,
                'message': 'Organization not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = OrganisationUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        organisation = OrganisationService.update(
            organisation=organisation,
            user=request.user,
            data=serializer.validated_data
        )
        
        # Refresh and eager load
        organisation = OrganisationSelector.get_by_id(request.user, organisation.id)
        
        return Response({
            'success': True,
            'message': 'Organization updated',
            'data': OrganisationDetailSerializer(organisation).data
        })
    
    def partial_update(self, request, pk=None):
        """PATCH /organisations/{id} - Same as update."""
        return self.update(request, pk)
    
    def destroy(self, request, pk=None):
        """
        DELETE /organisations/{id}
        
        Soft delete an organisation.
        Replicates Laravel's OrganisationController::destroy().
        """
        organisation = OrganisationSelector.get_by_id(request.user, pk)
        
        if not organisation:
            return Response({
                'success': False,
                'message': 'Organization not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        OrganisationService.delete(organisation, request.user)
        
        return Response({
            'success': True,
            'message': 'Organization deleted'
        })
    
    @action(detail=False, methods=['get', 'post'])
    def search(self, request):
        """
        GET/POST /organisations/search
        
        Search organisations.
        Replicates Laravel's OrganisationController::search().
        """
        search_value = request.query_params.get('search') or request.data.get('search', '')
        
        if not search_value or not search_value.strip():
            return self.list(request)
        
        queryset = OrganisationSelector.get_queryset(request.user)
        queryset = OrganisationSelector.filter_queryset(queryset, request.query_params)
        queryset = OrganisationSelector.search_queryset(queryset, search_value)
        queryset = OrganisationSelector.with_relations(queryset)
        
        serializer = OrganisationListSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'search_value': search_value,
        })
    
    @action(detail=False, methods=['get', 'post'])
    def filter(self, request):
        """
        GET/POST /organisations/filter
        
        Filter organisations (routes to index with filtering).
        Replicates Laravel's OrganisationController::index() with route filter.
        """
        return self.list(request)
    
    @action(detail=True, methods=['get'])
    def autocomplete(self, request, pk=None):
        """
        GET /organisations/{id}/autocomplete
        
        Get autocomplete data for an organisation.
        Replicates Laravel's OrganisationController::autocomplete().
        """
        organisation = OrganisationSelector.get_by_id(request.user, pk)
        
        if not organisation:
            return Response({
                'success': False,
                'message': 'Organization not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get primary address
        address = organisation.addresses.filter(primary=True).first()
        if not address:
            address = organisation.addresses.first()
        
        return Response({
            'address_line1': address.line1 if address else None,
            'address_line2': address.line2 if address else None,
            'address_line3': address.line3 if address else None,
            'address_city': address.city if address else None,
            'address_state': address.state if address else None,
            'address_code': address.code if address else None,
            'address_country': address.country if address else None,
        })
    
    def _build_page_link(self, request, page):
        """Build pagination link."""
        if page < 1:
            return None
        return f"{request.build_absolute_uri(request.path)}?page={page}"


class PersonViewSet(ViewSet):
    """
    ViewSet for persons.
    Replicates Laravel's PersonController.
    
    Endpoints:
        GET  /people              - List persons
        POST /people              - Create person
        GET  /people/{id}         - Get person
        PUT  /people/{id}         - Update person
        DELETE /people/{id}       - Delete person
        GET/POST /people/search   - Search persons
        POST /people/filter       - Filter persons
        GET  /people/{id}/autocomplete - Get autocomplete data
    """
    permission_classes = [IsAuthenticated, IsCRMUser]
    
    def list(self, request):
        """
        GET /people
        
        List persons with pagination, filtering, sorting.
        Replicates Laravel's PersonController::index().
        """
        user = request.user
        
        # Get base queryset with team scoping
        queryset = PersonSelector.get_queryset(user)
        
        # Apply filters
        queryset = PersonSelector.filter_queryset(queryset, request.query_params)
        
        # Apply search
        search = request.query_params.get('search', '')
        if search:
            queryset = PersonSelector.search_queryset(queryset, search)
        
        # Apply sorting
        sort = request.query_params.get('sort', 'created_at')
        direction = request.query_params.get('direction', 'desc')
        queryset = PersonSelector.sort_queryset(queryset, sort, direction)
        
        # Eager load relations
        queryset = PersonSelector.with_relations(queryset)
        
        # Pagination - matches Laravel's paginate(30)
        page = request.query_params.get('page', 1)
        per_page = request.query_params.get('per_page', 30)
        
        try:
            per_page = int(per_page)
            page = int(page)
        except (ValueError, TypeError):
            per_page = 30
            page = 1
        
        # If total count is less than per_page, return all without pagination
        total_count = queryset.count()
        
        if total_count <= per_page:
            serializer = PersonListSerializer(queryset, many=True)
            return Response({
                'success': True,
                'data': serializer.data,
                'meta': {
                    'current_page': 1,
                    'last_page': 1,
                    'per_page': per_page,
                    'total': total_count,
                }
            })
        
        # Paginate results
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        serializer = PersonListSerializer(page_obj, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {
                'current_page': page_obj.number,
                'last_page': paginator.num_pages,
                'per_page': per_page,
                'total': paginator.count,
            },
            'links': {
                'first': self._build_page_link(request, 1),
                'last': self._build_page_link(request, paginator.num_pages),
                'prev': self._build_page_link(request, page_obj.number - 1) if page_obj.has_previous() else None,
                'next': self._build_page_link(request, page_obj.number + 1) if page_obj.has_next() else None,
            }
        })
    
    def create(self, request):
        """POST /people - Create person."""
        serializer = PersonCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        person = PersonService.create(
            user=request.user,
            data=serializer.validated_data
        )
        
        # Refresh with relations
        person = PersonSelector.with_relations(
            PersonSelector.get_queryset(request.user)
        ).filter(id=person.id).first()
        
        return Response({
            'success': True,
            'message': 'Person stored',
            'data': PersonDetailSerializer(person).data
        }, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None):
        """GET /people/{id} - Get person."""
        person = PersonSelector.with_relations(
            PersonSelector.get_queryset(request.user)
        ).filter(id=pk).first()
        
        if not person:
            return Response({
                'success': False,
                'message': 'Person not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'data': PersonDetailSerializer(person).data
        })
    
    def update(self, request, pk=None):
        """PUT /people/{id} - Update person."""
        person = PersonSelector.get_queryset(request.user).filter(id=pk).first()
        
        if not person:
            return Response({
                'success': False,
                'message': 'Person not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PersonUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        person = PersonService.update(
            person=person,
            user=request.user,
            data=serializer.validated_data
        )
        
        # Refresh with relations
        person = PersonSelector.with_relations(
            PersonSelector.get_queryset(request.user)
        ).filter(id=person.id).first()
        
        return Response({
            'success': True,
            'message': 'Person updated',
            'data': PersonDetailSerializer(person).data
        })
    
    def partial_update(self, request, pk=None):
        """PATCH /people/{id}"""
        return self.update(request, pk)
    
    def destroy(self, request, pk=None):
        """DELETE /people/{id} - Soft delete person."""
        person = PersonSelector.get_queryset(request.user).filter(id=pk).first()
        
        if not person:
            return Response({
                'success': False,
                'message': 'Person not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        PersonService.delete(person, request.user)
        
        return Response({
            'success': True,
            'message': 'Person deleted'
        })
    
    @action(detail=False, methods=['get', 'post'])
    def search(self, request):
        """
        GET/POST /people/search
        
        Search persons.
        Replicates Laravel's PersonController::search().
        """
        search_value = request.query_params.get('search') or request.data.get('search', '')
        
        if not search_value or not search_value.strip():
            return self.list(request)
        
        queryset = PersonSelector.get_queryset(request.user)
        queryset = PersonSelector.filter_queryset(queryset, request.query_params)
        queryset = PersonSelector.search_queryset(queryset, search_value)
        queryset = PersonSelector.with_relations(queryset)
        
        serializer = PersonListSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'search_value': search_value,
        })
    
    @action(detail=False, methods=['get', 'post'])
    def filter(self, request):
        """
        GET/POST /people/filter
        
        Filter persons (routes to index with filtering).
        Replicates Laravel's PersonController::index() with route filter.
        """
        return self.list(request)
    
    @action(detail=True, methods=['get'])
    def autocomplete(self, request, pk=None):
        """
        GET /people/{id}/autocomplete
        
        Get autocomplete data for a person.
        Replicates Laravel's PersonController::autocomplete().
        Returns primary email and phone.
        """
        person = PersonSelector.with_relations(
            PersonSelector.get_queryset(request.user)
        ).filter(id=pk).first()
        
        if not person:
            return Response({
                'success': False,
                'message': 'Person not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get primary email
        email = person.emails.filter(primary=True).first()
        if not email:
            email = person.emails.first()
        
        # Get primary phone
        phone = person.phones.filter(primary=True).first()
        if not phone:
            phone = person.phones.first()
        
        return Response({
            'email': email.address if email else None,
            'email_type': email.type if email else None,
            'phone': phone.number if phone else None,
            'phone_type': phone.type if phone else None,
        })
    
    def _build_page_link(self, request, page):
        """Build pagination link."""
        if page < 1:
            return None
        return f"{request.build_absolute_uri(request.path)}?page={page}"


class LabelViewSet(ViewSet):
    """ViewSet for labels."""
    permission_classes = [IsAuthenticated, IsCRMUser]
    
    def list(self, request):
        """GET /labels - List labels."""
        queryset = LabelSelector.get_queryset(request.user)
        serializer = LabelSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })


class OrganisationTypeViewSet(ViewSet):
    """ViewSet for organisation types."""
    permission_classes = [IsAuthenticated, IsCRMUser]
    
    def list(self, request):
        """GET /organisation-types - List organisation types."""
        queryset = OrganisationTypeSelector.get_queryset(request.user)
        serializer = OrganisationTypeSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })


class IndustryViewSet(ViewSet):
    """ViewSet for industries."""
    permission_classes = [IsAuthenticated, IsCRMUser]
    
    def list(self, request):
        """GET /industries - List industries."""
        queryset = IndustrySelector.get_queryset(request.user)
        serializer = IndustrySerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })


# ============================================================================
# LEAD, PIPELINE & DEAL VIEWS
# ============================================================================


class PipelineViewSet(ViewSet):
    """
    ViewSet for pipelines.
    Replicates Laravel's PipelineController.
    """
    permission_classes = [IsAuthenticated, IsCRMUser]
    
    def list(self, request):
        """GET /pipelines - List pipelines."""
        queryset = PipelineSelector.get_queryset(request.user)
        
        # Filter by model type
        model_type = request.query_params.get('model')
        if model_type:
            queryset = queryset.filter(model=model_type)
        
        queryset = PipelineSelector.with_stages(queryset)
        
        # Use full serializer to include stages
        include_stages = request.query_params.get('include_stages', 'true').lower() == 'true'
        if include_stages:
            serializer = PipelineSerializer(queryset, many=True)
        else:
            serializer = PipelineListSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def retrieve(self, request, pk=None):
        """GET /pipelines/{id} - Get pipeline."""
        try:
            queryset = PipelineSelector.get_queryset(request.user)
            queryset = PipelineSelector.with_stages(queryset)
            pipeline = queryset.get(pk=pk)
        except Pipeline.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Pipeline not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PipelineSerializer(pipeline)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def create(self, request):
        """POST /pipelines - Create pipeline."""
        serializer = PipelineCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        pipeline = PipelineService.create(request.user, serializer.validated_data)
        
        return Response({
            'success': True,
            'data': PipelineSerializer(pipeline).data,
            'message': 'Pipeline created successfully'
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk=None):
        """PUT /pipelines/{id} - Update pipeline."""
        try:
            pipeline = PipelineSelector.get_queryset(request.user).get(pk=pk)
        except Pipeline.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Pipeline not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PipelineUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        pipeline = PipelineService.update(pipeline, request.user, serializer.validated_data)
        
        return Response({
            'success': True,
            'data': PipelineSerializer(pipeline).data,
            'message': 'Pipeline updated successfully'
        })
    
    def destroy(self, request, pk=None):
        """DELETE /pipelines/{id} - Delete pipeline."""
        try:
            pipeline = PipelineSelector.get_queryset(request.user).get(pk=pk)
        except Pipeline.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Pipeline not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        PipelineService.delete(pipeline, request.user)
        
        return Response({
            'success': True,
            'message': 'Pipeline deleted successfully'
        })


class PipelineStageViewSet(ViewSet):
    """
    ViewSet for pipeline stages.
    Replicates Laravel's PipelineStageController.
    """
    permission_classes = [IsAuthenticated, IsCRMUser]
    
    def list(self, request):
        """GET /pipeline-stages - List pipeline stages."""
        queryset = PipelineStageSelector.get_queryset(request.user)
        
        # Filter by pipeline
        pipeline_id = request.query_params.get('pipeline_id')
        if pipeline_id:
            queryset = queryset.filter(pipeline_id=pipeline_id)
        
        serializer = PipelineStageSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def create(self, request):
        """POST /pipeline-stages - Create pipeline stage."""
        serializer = PipelineStageCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        stage = PipelineStageService.create(request.user, serializer.validated_data)
        
        return Response({
            'success': True,
            'data': PipelineStageSerializer(stage).data,
            'message': 'Pipeline stage created successfully'
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk=None):
        """PUT /pipeline-stages/{id} - Update pipeline stage."""
        try:
            stage = PipelineStageSelector.get_queryset(request.user).get(pk=pk)
        except PipelineStage.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Pipeline stage not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PipelineStageUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        stage = PipelineStageService.update(stage, request.user, serializer.validated_data)
        
        return Response({
            'success': True,
            'data': PipelineStageSerializer(stage).data,
            'message': 'Pipeline stage updated successfully'
        })
    
    def destroy(self, request, pk=None):
        """DELETE /pipeline-stages/{id} - Delete pipeline stage."""
        try:
            stage = PipelineStageSelector.get_queryset(request.user).get(pk=pk)
        except PipelineStage.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Pipeline stage not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        PipelineStageService.delete(stage, request.user)
        
        return Response({
            'success': True,
            'message': 'Pipeline stage deleted successfully'
        })


class LeadStatusViewSet(ViewSet):
    """ViewSet for lead statuses."""
    permission_classes = [IsAuthenticated, IsCRMUser]
    
    def list(self, request):
        """GET /lead-statuses - List lead statuses."""
        queryset = LeadStatusSelector.get_queryset(request.user)
        serializer = LeadStatusSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })


class LeadSourceViewSet(ViewSet):
    """ViewSet for lead sources."""
    permission_classes = [IsAuthenticated, IsCRMUser]
    
    def list(self, request):
        """GET /lead-sources - List lead sources."""
        queryset = LeadSourceSelector.get_queryset(request.user)
        serializer = LeadSourceSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })


class DealViewSet(ViewSet):
    """
    ViewSet for deals.
    Replicates Laravel's DealController.
    
    Endpoints:
        GET    /deals               - List deals
        POST   /deals               - Create deal
        GET    /deals/{id}          - Get deal
        PUT    /deals/{id}          - Update deal
        DELETE /deals/{id}          - Delete deal
        POST   /deals/{id}/close    - Close deal as won/lost
        POST   /deals/{id}/reopen   - Reopen closed deal
        POST   /deals/{id}/move     - Move deal to different stage
        GET    /deals/search        - Search deals
    """
    permission_classes = [IsAuthenticated, IsCRMUser]
    
    def list(self, request):
        """GET /deals - List deals with pagination, filtering, sorting."""
        user = request.user
        
        # Get base queryset
        include_closed = request.query_params.get('include_closed', 'true').lower() == 'true'
        queryset = DealSelector.get_queryset(user, include_closed=include_closed)
        
        # Apply filters
        queryset = DealSelector.filter_queryset(queryset, request.query_params)
        
        # Apply search
        search = request.query_params.get('search', '')
        if search:
            queryset = DealSelector.search_queryset(queryset, search)
        
        # Apply sorting
        sort = request.query_params.get('sort', 'created_at')
        direction = request.query_params.get('direction', 'desc')
        queryset = DealSelector.sort_queryset(queryset, sort, direction)
        
        # Eager load relations
        queryset = DealSelector.with_relations(queryset)
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 30))
        
        total_count = queryset.count()
        
        if total_count <= per_page:
            serializer = DealListSerializer(queryset, many=True)
            return Response({
                'success': True,
                'data': serializer.data,
                'meta': {
                    'current_page': 1,
                    'last_page': 1,
                    'per_page': per_page,
                    'total': total_count,
                }
            })
        
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        serializer = DealListSerializer(page_obj.object_list, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {
                'current_page': page,
                'last_page': paginator.num_pages,
                'per_page': per_page,
                'total': paginator.count,
            }
        })
    
    def retrieve(self, request, pk=None):
        """GET /deals/{id} - Get deal details."""
        try:
            queryset = DealSelector.get_queryset(request.user, include_closed=True)
            queryset = DealSelector.with_relations(queryset)
            deal = queryset.get(pk=pk)
        except Deal.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Deal not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = DealSerializer(deal)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def create(self, request):
        """POST /leads - Create lead."""
        serializer = LeadCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        data = serializer.validated_data
        
        # Get related objects
        person = None
        organisation = None
        if data.get('person_id'):
            person = Person.objects.filter(pk=data['person_id']).first()
        if data.get('organisation_id'):
            organisation = Organisation.objects.filter(pk=data['organisation_id']).first()
        
        lead = LeadService.create(request.user, data, person=person, organisation=organisation)
        
        return Response({
            'success': True,
            'data': LeadSerializer(lead).data,
            'message': 'Lead created successfully'
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk=None):
        """PUT /leads/{id} - Update lead."""
        try:
            lead = LeadSelector.get_queryset(request.user, include_converted=True).get(pk=pk)
        except Lead.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Lead not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = LeadUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        data = serializer.validated_data
        
        # Get related objects
        person = None
        organisation = None
        if 'person_id' in data:
            person = Person.objects.filter(pk=data['person_id']).first() if data['person_id'] else None
        if 'organisation_id' in data:
            organisation = Organisation.objects.filter(pk=data['organisation_id']).first() if data['organisation_id'] else None
        
        lead = LeadService.update(lead, request.user, data, person=person, organisation=organisation)
        
        return Response({
            'success': True,
            'data': LeadSerializer(lead).data,
            'message': 'Lead updated successfully'
        })
    
    def destroy(self, request, pk=None):
        """DELETE /leads/{id} - Delete lead."""
        try:
            lead = LeadSelector.get_queryset(request.user, include_converted=True).get(pk=pk)
        except Lead.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Lead not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        LeadService.delete(lead, request.user)
        
        return Response({
            'success': True,
            'message': 'Lead deleted successfully'
        })
    
    @action(detail=True, methods=['post'])
    def convert(self, request, pk=None):
        """POST /leads/{id}/convert - Convert lead to deal."""
        try:
            lead = LeadSelector.get_queryset(request.user).get(pk=pk)
        except Lead.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Lead not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if lead.converted_at:
            return Response({
                'success': False,
                'message': 'Lead has already been converted'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = LeadConvertSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        data = serializer.validated_data
        
        # Get related objects
        person = None
        organisation = None
        if data.get('person_id'):
            person = Person.objects.filter(pk=data['person_id']).first()
        if data.get('organisation_id'):
            organisation = Organisation.objects.filter(pk=data['organisation_id']).first()
        
        deal = LeadService.convert_to_deal(lead, request.user, data, person=person, organisation=organisation)
        
        return Response({
            'success': True,
            'data': DealSerializer(deal).data,
            'message': 'Lead converted to deal successfully'
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """GET /leads/search - Search leads for autocomplete."""
        search = request.query_params.get('q', '')
        limit = int(request.query_params.get('limit', 10))
        
        queryset = LeadSelector.get_queryset(request.user)
        if search:
            queryset = LeadSelector.search_queryset(queryset, search)
        
        queryset = queryset[:limit]
        serializer = LeadListSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })


class DealViewSet(ViewSet):
    """
    ViewSet for deals.
    Replicates Laravel's DealController.
    
    Endpoints:
        GET    /deals               - List deals
        POST   /deals               - Create deal
        GET    /deals/{id}          - Get deal
        PUT    /deals/{id}          - Update deal
        DELETE /deals/{id}          - Delete deal
        POST   /deals/{id}/close    - Close deal as won/lost
        POST   /deals/{id}/reopen   - Reopen closed deal
        POST   /deals/{id}/move     - Move deal to different stage
        GET    /deals/search        - Search deals
    """
    permission_classes = [IsAuthenticated, IsCRMUser]
    
    def list(self, request):
        """GET /deals - List deals with pagination, filtering, sorting."""
        user = request.user
        
        # Get base queryset
        include_closed = request.query_params.get('include_closed', 'true').lower() == 'true'
        queryset = DealSelector.get_queryset(user, include_closed=include_closed)
        
        # Apply filters
        queryset = DealSelector.filter_queryset(queryset, request.query_params)
        
        # Apply search
        search = request.query_params.get('search', '')
        if search:
            queryset = DealSelector.search_queryset(queryset, search)
        
        # Apply sorting
        sort = request.query_params.get('sort', 'created_at')
        direction = request.query_params.get('direction', 'desc')
        queryset = DealSelector.sort_queryset(queryset, sort, direction)
        
        # Eager load relations
        queryset = DealSelector.with_relations(queryset)
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 30))
        
        total_count = queryset.count()
        
        if total_count <= per_page:
            serializer = DealListSerializer(queryset, many=True)
            return Response({
                'success': True,
                'data': serializer.data,
                'meta': {
                    'current_page': 1,
                    'last_page': 1,
                    'per_page': per_page,
                    'total': total_count,
                }
            })
        
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        serializer = DealListSerializer(page_obj.object_list, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {
                'current_page': page,
                'last_page': paginator.num_pages,
                'per_page': per_page,
                'total': paginator.count,
            }
        })
    
    def retrieve(self, request, pk=None):
        """GET /deals/{id} - Get deal details."""
        try:
            queryset = DealSelector.get_queryset(request.user)
            queryset = DealSelector.with_relations(queryset)
            deal = queryset.get(pk=pk)
        except Deal.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Deal not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = DealSerializer(deal)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def create(self, request):
        """POST /deals - Create deal."""
        serializer = DealCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        data = serializer.validated_data
        
        # Get related objects
        person = None
        organisation = None
        if data.get('person_id'):
            person = Person.objects.filter(pk=data['person_id']).first()
        if data.get('organisation_id'):
            organisation = Organisation.objects.filter(pk=data['organisation_id']).first()
        
        deal = DealService.create(request.user, data, person=person, organisation=organisation)
        
        return Response({
            'success': True,
            'data': DealSerializer(deal).data,
            'message': 'Deal created successfully'
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk=None):
        """PUT /deals/{id} - Update deal."""
        try:
            deal = DealSelector.get_queryset(request.user).get(pk=pk)
        except Deal.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Deal not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = DealUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Get related objects
        person = None
        organisation = None
        if 'person_id' in data:
            person = Person.objects.filter(pk=data['person_id']).first() if data['person_id'] else None
        if 'organisation_id' in data:
            organisation = Organisation.objects.filter(pk=data['organisation_id']).first() if data['organisation_id'] else None
        
        deal = DealService.update(deal, request.user, data, person=person, organisation=organisation)
        
        return Response({
            'success': True,
            'data': DealSerializer(deal).data,
            'message': 'Deal updated successfully'
        })
    
    def partial_update(self, request, pk=None):
        """PATCH /deals/{id} - Partial update deal."""
        # PATCH and PUT use the same logic for this implementation
        return self.update(request, pk)
    
    def destroy(self, request, pk=None):
        """DELETE /deals/{id} - Delete deal."""
        try:
            deal = DealSelector.get_queryset(request.user).get(pk=pk)
        except Deal.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Deal not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        DealService.delete(deal, request.user)
        
        return Response({
            'success': True,
            'message': 'Deal deleted successfully'
        })
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """POST /deals/{id}/close - Close deal as won/lost."""
        try:
            deal = DealSelector.get_queryset(request.user).get(pk=pk)
        except Deal.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Deal not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if deal.closed_status:
            return Response({
                'success': False,
                'message': 'Deal is already closed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = DealCloseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        deal = DealService.close_deal(
            deal,
            request.user,
            serializer.validated_data['status'],
            serializer.validated_data.get('closed_at')
        )
        
        return Response({
            'success': True,
            'data': DealSerializer(deal).data,
            'message': f'Deal marked as {deal.closed_status}'
        })
    
    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        """POST /deals/{id}/reopen - Reopen closed deal."""
        try:
            deal = DealSelector.get_queryset(request.user).get(pk=pk)
        except Deal.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Deal not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if not deal.closed_status:
            return Response({
                'success': False,
                'message': 'Deal is not closed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        deal = DealService.reopen_deal(deal, request.user)
        
        return Response({
            'success': True,
            'data': DealSerializer(deal).data,
            'message': 'Deal reopened successfully'
        })
    
    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        """POST /deals/{id}/move - Move deal to different stage."""
        try:
            deal = DealSelector.get_queryset(request.user).get(pk=pk)
        except Deal.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Deal not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        stage_id = request.data.get('pipeline_stage_id')
        if not stage_id:
            return Response({
                'success': False,
                'message': 'pipeline_stage_id is required'
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        try:
            deal = DealService.move_to_stage(deal, stage_id, request.user)
        except ValueError as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': True,
            'data': DealSerializer(deal).data,
            'message': 'Deal moved to new stage'
        })
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """GET /deals/search - Search deals for autocomplete."""
        search = request.query_params.get('q', '')
        limit = int(request.query_params.get('limit', 10))
        
        queryset = DealSelector.get_queryset(request.user)
        if search:
            queryset = DealSelector.search_queryset(queryset, search)
        
        queryset = queryset[:limit]
        serializer = DealListSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
