from django.db import transaction
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from apps.crm.models import Label, Note
from apps.crm.serializers import UserMiniSerializer
from apps.pipeline.models import Deal


class LeadService:
    """Service class for Lead business logic."""
    
    @staticmethod
    def create_lead(user, data):
        """Create a new lead with business logic."""
        from .models import Lead
        from .serializers import LeadCreateSerializer
        
        # Create a mock request object if user is None
        if user is None:
            mock_request = type('Request', (), {'user': None})()
            context = {'request': mock_request}
        else:
            context = {'request': type('Request', (), {'user': user})()}
        
        serializer = LeadCreateSerializer(data=data, context=context)
        if serializer.is_valid():
            lead = serializer.save()
            
            # Log activity
            LeadService._log_activity(user, lead, 'created')
            
            return lead
        else:
            raise ValueError(serializer.errors)
    
    @staticmethod
    def update_lead(user, lead, data):
        """Update a lead with business logic."""
        from .serializers import LeadUpdateSerializer
        
        # Create a mock request object if user is None
        if user is None:
            mock_request = type('Request', (), {'user': None})()
            context = {'request': mock_request}
        else:
            context = {'request': type('Request', (), {'user': user})()}
        
        serializer = LeadUpdateSerializer(
            lead, 
            data=data, 
            partial=True,
            context=context
        )
        if serializer.is_valid():
            updated_lead = serializer.save()
            
            # Log activity
            LeadService._log_activity(user, updated_lead, 'updated')
            
            return updated_lead
        else:
            raise ValueError(serializer.errors)
    
    @staticmethod
    def delete_lead(user, lead):
        """Soft delete a lead."""
        lead.soft_delete(user)  # Pass User instance, not ID
        
        # Log activity
        LeadService._log_activity(user, lead, 'deleted')
    
    @staticmethod
    def restore_lead(user, lead):
        """Restore a soft deleted lead."""
        lead.restore(user)  # Pass User instance, not ID
        
        # Log activity
        LeadService._log_activity(user, lead, 'restored')
    
    @staticmethod
    def convert_lead_to_deal(user, lead, conversion_data=None):
        """Convert a lead to a deal."""
        if lead.converted_at:
            raise ValueError("Lead has already been converted.")
        
        conversion_data = conversion_data or {}
        
        with transaction.atomic():
            # Create deal from lead
            deal = Deal.objects.create(
                external_id=lead.external_id,
                team_id=lead.team_id,
                lead=lead,  # Establish the lead relationship
                person_id=lead.person_id,
                organisation_id=lead.organisation_id,
                pipeline_id=lead.pipeline_id,
                pipeline_stage_id=lead.pipeline_stage_id,
                title=conversion_data.get('name', lead.title),
                description=lead.description,
                amount=conversion_data.get('amount', lead.amount),
                currency=lead.currency,
                expected_close=lead.expected_close,
                user_created=user if user else None,
                user_updated=user if user else None,
                user_owner=user if user else None,
                user_assigned=user if user else None,
            )
            
            # Mark lead as converted
            lead.converted_at = timezone.now()
            lead.user_updated_id = user.id if user else None
            lead.save()
            
            # Copy labels from lead to deal
            for label in lead.labels.all():
                deal.labels.add(label)
            
            # Log activity
            LeadService._log_activity(user, lead, 'converted_to_deal')
            
            return deal
    
    @staticmethod
    def assign_labels(user, lead, label_ids):
        """Assign labels to a lead."""
        lead_content_type = ContentType.objects.get_for_model(Lead)
        
        # Clear existing labels
        lead.labels.clear()
        
        # Assign new labels
        for label_id in label_ids:
            try:
                label = Label.objects.get(id=label_id)
                lead.labels.add(label)
            except Label.DoesNotExist:
                continue
        
        # Log activity
        LeadService._log_activity(user, lead, 'labels_updated')
    
    @staticmethod
    def add_note(user, lead, note_content):
        """Add a note to a lead."""
        note = Note.objects.create(
            content=note_content,
            user_created_id=user.id if user else None,
            content_type=ContentType.objects.get_for_model(Lead),
            object_id=lead.id
        )
        
        # Log activity
        LeadService._log_activity(user, lead, 'note_added')
        
        return note
    
    @staticmethod
    def bulk_update_status(user, lead_ids, status_id):
        """Bulk update lead status."""
        from .models import Lead
        
        updated_count = Lead.objects.filter(
            id__in=lead_ids,
            is_deleted=False
        ).update(
            lead_status_id=status_id,
            user_updated_id=user.id if user else None,
            updated_at=timezone.now()
        )
        
        # Log activity for each lead
        if user:  # Only log if user is not None
            for lead in Lead.objects.filter(id__in=lead_ids):
                LeadService._log_activity(user, lead, 'bulk_status_updated')
        
        return updated_count
    
    @staticmethod
    def bulk_assign(user, lead_ids, assigned_user_id):
        """Bulk assign leads to user."""
        from .models import Lead
        
        updated_count = Lead.objects.filter(
            id__in=lead_ids,
            is_deleted=False
        ).update(
            user_assigned_id=assigned_user_id,
            user_updated_id=user.id if user else None,
            updated_at=timezone.now()
        )
        
        # Log activity for each lead
        if user:  # Only log if user is not None
            for lead in Lead.objects.filter(id__in=lead_ids):
                LeadService._log_activity(user, lead, 'bulk_assigned')
        
        return updated_count
    
    @staticmethod
    def bulk_delete(user, lead_ids):
        """Bulk delete leads (soft delete)."""
        from .models import Lead
        
        deleted_count = Lead.objects.filter(
            id__in=lead_ids,
            is_deleted=False
        ).update(
            is_deleted=True,
            deleted_at=timezone.now(),
            user_updated_id=user.id if user else None,
            updated_at=timezone.now()
        )
        
        # Log activity for each lead
        if user:  # Only log if user is not None
            for lead in Lead.objects.filter(id__in=lead_ids):
                LeadService._log_activity(user, lead, 'bulk_deleted')
        
        return deleted_count
    
    @staticmethod
    def _log_activity(user, lead, action):
        """Log activity for lead operations."""
        # TODO: Implement Activity model in apps.crm.models
        # from apps.crm.models import Activity
        
        # Skip activity logging if user is None (testing mode)
        if user is None:
            return
        
        # Temporarily disabled until Activity model is implemented
        pass


# Import models at the end to avoid circular imports
from .models import Lead
