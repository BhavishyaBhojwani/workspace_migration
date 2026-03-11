from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

from apps.accounts.permissions import IsCRMUser
from apps.crm.models import Label, Note
from .models import Lead, LeadStatus, LeadSource
from .selectors import LeadSelector
from .services import LeadService
from .serializers import (
    LeadListSerializer, LeadSerializer, LeadEditSerializer, LeadCreateSerializer,
    LeadConvertSerializer, LeadStatusSerializer,
    LeadSourceSerializer
)


class LeadViewSet(ViewSet):
    """
    ViewSet for leads.
    Replicates Laravel's LeadController behavior.
    
    Endpoints:
        GET    /leads               - List leads (with search, filter, sort)
        POST   /leads               - Create lead
        GET    /leads/{id}          - Get lead
        PUT    /leads/{id}          - Update lead
        DELETE /leads/{id}          - Delete lead
        POST   /leads/{id}/convert  - Convert lead to deal
        POST   /leads/{id}/labels   - Assign labels
        POST   /leads/{id}/notes    - Add note
        POST   /leads/bulk-status   - Bulk update status
        POST   /leads/bulk-assign   - Bulk assign
    """
    permission_classes = [IsAuthenticated, IsCRMUser]
    
    def list(self, request):
        """GET /leads - List leads with pagination, filtering, sorting."""
        user = request.user
        
        # Get base queryset
        include_converted = request.query_params.get('include_converted', 'false').lower() == 'true'
        queryset = LeadSelector.get_queryset(user, include_converted=include_converted)
        
        # Apply filters
        queryset = LeadSelector.filter_queryset(queryset, request.query_params)
        
        # Apply search
        search = request.query_params.get('search', '')
        if search:
            queryset = LeadSelector.search_queryset(queryset, search)
        
        # Apply sorting
        sort = request.query_params.get('sort', 'created_at')
        direction = request.query_params.get('direction', 'desc')
        queryset = LeadSelector.sort_queryset(queryset, sort, direction)
        
        # Eager load relations
        queryset = LeadSelector.with_relations(queryset)
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 30))
        
        total_count = queryset.count()
        
        if total_count <= per_page:
            serializer = LeadListSerializer(queryset, many=True)
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
        
        serializer = LeadListSerializer(page_obj.object_list, many=True)
        
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
        """GET /leads/{id} - Get lead details."""
        queryset = LeadSelector.get_queryset(None, include_converted=True)
        queryset = LeadSelector.with_relations(queryset)
        lead = get_object_or_404(queryset, pk=pk)
        
        serializer = LeadSerializer(lead)
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
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        lead = LeadService.create_lead(request.user, request.data)
        serializer = LeadSerializer(lead)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Lead created successfully'
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk=None):
        """PUT /leads/{id} - Update lead."""
        queryset = LeadSelector.get_queryset(request.user)
        lead = get_object_or_404(queryset, pk=pk)
        
        try:
            updated_lead = LeadService.update_lead(request.user, lead, request.data)
            serializer = LeadSerializer(updated_lead)
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Lead updated successfully'
            })
        except ValueError as e:
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': e.args[0] if isinstance(e.args[0], dict) else str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, pk=None):
        """PATCH /leads/{id} - Partial update lead."""
        # PATCH and PUT use the same logic for this implementation
        return self.update(request, pk)
    
    def destroy(self, request, pk=None):
        """DELETE /leads/{id} - Delete lead."""
        queryset = LeadSelector.get_queryset(request.user)
        lead = get_object_or_404(queryset, pk=pk)
        
        LeadService.delete_lead(request.user, lead)
        return Response({
            'success': True,
            'message': 'Lead deleted successfully'
        })
    
    @action(detail=True, methods=['post'])
    def convert(self, request, pk=None):
        """POST /leads/{id}/convert - Convert lead to deal."""
        queryset = LeadSelector.get_queryset(request.user)
        lead = get_object_or_404(queryset, pk=pk)
        
        # Accept frontend data for deal customization
        serializer = LeadConvertSerializer(data=request.data, context={'lead': lead})
        if serializer.is_valid():
            try:
                deal = LeadService.convert_lead_to_deal(request.user, lead, request.data)
                return Response({
                    'success': True,
                    'data': {'deal_id': deal.id},
                    'message': 'Lead converted to deal successfully'
                })
            except ValueError as e:
                return Response({
                    'success': False,
                    'message': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def labels(self, request, pk=None):
        """POST /leads/{id}/labels - Assign labels to lead."""
        queryset = LeadSelector.get_queryset(request.user)
        lead = get_object_or_404(queryset, pk=pk)
        
        label_ids = request.data.get('label_ids', [])
        LeadService.assign_labels(request.user, lead, label_ids)
        
        return Response({
            'success': True,
            'message': 'Labels assigned successfully'
        })
    
    @action(detail=True, methods=['post'])
    def notes(self, request, pk=None):
        """POST /leads/{id}/notes - Add note to lead."""
        queryset = LeadSelector.get_queryset(request.user)
        lead = get_object_or_404(queryset, pk=pk)
        
        note_content = request.data.get('content', '')
        if not note_content:
            return Response({
                'success': False,
                'message': 'Note content is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        note = LeadService.add_note(request.user, lead, note_content)
        
        return Response({
            'success': True,
            'data': {
                'note_id': note.id,
                'content': note.content,
                'created_at': note.created_at
            },
            'message': 'Note added successfully'
        })
    
    @action(detail=False, methods=['post'])
    def bulk_status(self, request):
        """POST /leads/bulk-status - Bulk update lead status."""
        lead_ids = request.data.get('lead_ids', [])
        status_id = request.data.get('status_id')
        
        if not lead_ids or not status_id:
            return Response({
                'success': False,
                'message': 'lead_ids and status_id are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        updated_count = LeadService.bulk_update_status(request.user, lead_ids, status_id)
        
        return Response({
            'success': True,
            'data': {'updated_count': updated_count},
            'message': f'{updated_count} leads updated successfully'
        })
    
    @action(detail=False, methods=['post'])
    def bulk_assign(self, request):
        """POST /leads/bulk-assign - Bulk assign leads to user."""
        lead_ids = request.data.get('lead_ids', [])
        assigned_user_id = request.data.get('assigned_user_id')
        
        if not lead_ids or not assigned_user_id:
            return Response({
                'success': False,
                'message': 'lead_ids and assigned_user_id are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        updated_count = LeadService.bulk_assign(request.user, lead_ids, assigned_user_id)
        
        return Response({
            'success': True,
            'data': {'updated_count': updated_count},
            'message': f'{updated_count} leads assigned successfully'
        })
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """POST /leads/bulk-delete - Bulk delete leads."""
        lead_ids = request.data.get('lead_ids', [])
        
        if not lead_ids:
            return Response({
                'success': False,
                'message': 'lead_ids are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        deleted_count = LeadService.bulk_delete(request.user, lead_ids)
        
        return Response({
            'success': True,
            'data': {'deleted_count': deleted_count},
            'message': f'{deleted_count} leads deleted successfully'
        })


class LeadStatusViewSet(ViewSet):
    """ViewSet for lead statuses."""
    # permission_classes = [IsAuthenticated, IsCRMUser]  # Temporarily disabled for testing
    
    def list(self, request):
        """GET /lead-statuses - List lead statuses."""
        statuses = LeadStatus.objects.filter(is_deleted=False)
        serializer = LeadStatusSerializer(statuses, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def retrieve(self, request, pk=None):
        """GET /lead-statuses/{id} - Get lead status."""
        status = get_object_or_404(LeadStatus, pk=pk, is_deleted=False)
        serializer = LeadStatusSerializer(status)
        return Response({
            'success': True,
            'data': serializer.data
        })


class LeadSourceViewSet(ViewSet):
    """ViewSet for lead sources."""
    # permission_classes = [IsAuthenticated, IsCRMUser]  # Temporarily disabled for testing
    
    def list(self, request):
        """GET /lead-sources - List lead sources."""
        sources = LeadSource.objects.filter(is_deleted=False)
        serializer = LeadSourceSerializer(sources, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def retrieve(self, request, pk=None):
        """GET /lead-sources/{id} - Get lead source."""
        source = get_object_or_404(LeadSource, pk=pk, is_deleted=False)
        serializer = LeadSourceSerializer(source)
        return Response({
            'success': True,
            'data': serializer.data
        })
