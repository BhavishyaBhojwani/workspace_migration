from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from apps.crm.serializers import (
    PersonListSerializer, OrganisationListSerializer, UserMiniSerializer
)
from apps.crm.models import Person, Organisation
from .models import Lead, LeadStatus, LeadSource

User = get_user_model()


class LeadStatusSerializer(serializers.ModelSerializer):
    """Serializer for LeadStatus model."""
    
    class Meta:
        model = LeadStatus
        fields = '__all__'


class LeadSourceSerializer(serializers.ModelSerializer):
    """Serializer for LeadSource model."""
    
    class Meta:
        model = LeadSource
        fields = '__all__'


class LeadListSerializer(serializers.ModelSerializer):
    """Serializer for Lead list view with minimal fields."""
    person_name = serializers.CharField(source='person.first_name', read_only=True)
    person_last_name = serializers.CharField(source='person.last_name', read_only=True)
    organisation_name = serializers.CharField(source='organisation.name', read_only=True)
    lead_status_name = serializers.CharField(source='lead_status.name', read_only=True)
    lead_source_name = serializers.CharField(source='lead_source.name', read_only=True)
    owner_name = serializers.CharField(source='user_owner.name', read_only=True)
    assigned_name = serializers.CharField(source='user_assigned.name', read_only=True)
    amount_display = serializers.SerializerMethodField()
    labels = serializers.SerializerMethodField()
    
    class Meta:
        model = Lead
        fields = [
            'id', 'external_id', 'title', 'person_name', 'person_last_name',
            'organisation_name', 'lead_status_name', 'lead_source_name',
            'amount', 'amount_display', 'currency', 'qualified', 'expected_close', 'converted_at',
            'owner_name', 'assigned_name', 'created_at', 'updated_at', 'labels'
        ]
    
    def get_amount_display(self, obj):
        if obj.amount:
            return float(obj.amount)
        return None
    
    def get_labels(self, obj):
        """Return labels as a comma-separated string for display."""
        try:
            labels = obj.labels.all()
            return ', '.join([label.name for label in labels]) if labels else ''
        except Exception:
            # Handle GenericRelation access issues
            return ''


class LeadSerializer(serializers.ModelSerializer):
    """Detailed serializer for Lead model."""
    person = PersonListSerializer(read_only=True)
    organisation = OrganisationListSerializer(read_only=True)
    lead_status = LeadStatusSerializer(read_only=True)
    lead_source = LeadSourceSerializer(read_only=True)
    user_created = UserMiniSerializer(read_only=True)
    user_updated = UserMiniSerializer(read_only=True)
    user_owner = UserMiniSerializer(read_only=True)
    user_assigned = UserMiniSerializer(read_only=True)
    
    class Meta:
        model = Lead
        fields = '__all__'


class LeadEditSerializer(serializers.Serializer):
    """Serializer for lead edit form that returns IDs for dropdown compatibility."""
    id = serializers.IntegerField(read_only=True)
    external_id = serializers.CharField(read_only=True)
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True, allow_null=True)
    person = serializers.SerializerMethodField()
    organisation = serializers.SerializerMethodField()
    lead_status = serializers.SerializerMethodField()
    lead_source = serializers.SerializerMethodField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    currency = serializers.CharField(max_length=3)
    qualified = serializers.BooleanField()
    expected_close = serializers.DateTimeField(allow_null=True)
    user_owner = UserMiniSerializer(read_only=True)
    user_assigned = UserMiniSerializer(read_only=True)
    
    def get_person(self, obj):
        return obj.person.id if obj.person else None
    
    def get_organisation(self, obj):
        return obj.organisation.id if obj.organisation else None
    
    def get_lead_status(self, obj):
        return obj.lead_status.id if obj.lead_status else None
    
    def get_lead_source(self, obj):
        return obj.lead_source.id if obj.lead_source else None


class LeadCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Lead with validation."""
    person = serializers.PrimaryKeyRelatedField(queryset=Person.objects.all(), allow_null=True, required=False)
    organisation = serializers.PrimaryKeyRelatedField(queryset=Organisation.objects.all(), allow_null=True, required=False)
    lead_status = serializers.PrimaryKeyRelatedField(queryset=LeadStatus.objects.all(), allow_null=True, required=False)
    lead_source = serializers.PrimaryKeyRelatedField(queryset=LeadSource.objects.all(), allow_null=True, required=False)
    user_owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True, required=False)
    user_assigned = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True, required=False)
    labels = serializers.CharField(allow_blank=True, required=False)
    
    class Meta:
        model = Lead
        fields = [
            'title', 'description', 'person', 'organisation',
            'amount', 'currency', 'lead_status', 'lead_source',
            'qualified', 'expected_close', 'user_owner', 'user_assigned', 'labels'
        ]
    
    def validate_title(self, value):
        """Validate title is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Title is required.")
        return value.strip()
    
    def validate_amount(self, value):
        """Validate amount is positive."""
        if value is not None and value < 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value
    
    def validate_currency(self, value):
        """Validate currency code."""
        valid_currencies = ['USD', 'EUR', 'GBP', 'INR']
        if value not in valid_currencies:
            raise serializers.ValidationError(f"Currency must be one of: {', '.join(valid_currencies)}")
        return value
    
    def validate(self, attrs):
        """Cross-field validation."""
        # Ensure either person or organisation is provided
        person = attrs.get('person')
        organisation = attrs.get('organisation')
        
        if not person and not organisation:
            raise serializers.ValidationError(
                "Either person or organisation must be provided."
            )
        
        return attrs
    
    def create(self, validated_data):
        """Create lead with user tracking and labels."""
        user = self.context['request'].user
        validated_data['user_created'] = user
        validated_data['user_updated'] = user
        
        # Set default owner if not provided
        if 'user_owner' not in validated_data:
            validated_data['user_owner'] = user
        
        # Extract labels from validated_data
        labels_str = validated_data.pop('labels', '')
        
        # Create the lead
        lead = super().create(validated_data)
        
        # Process labels if provided
        if labels_str and labels_str.strip():
            from apps.crm.models import Label
            label_names = [name.strip() for name in labels_str.split(',') if name.strip()]
            
            for label_name in label_names:
                # Get or create label
                label, created = Label.objects.get_or_create(
                    name=label_name,
                    defaults={
                        'team_id': user.profile.team_id if hasattr(user, 'profile') else None,
                        'user_created': user,
                        'user_updated': user
                    }
                )
                
                # Add label to lead
                lead.labels.add(label)
        
        return lead


class LeadUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating Lead."""
    
    class Meta:
        model = Lead
        fields = [
            'title', 'description', 'person_id', 'organisation_id',
            'amount', 'currency', 'lead_status_id', 'lead_source_id',
            'qualified', 'expected_close', 'user_owner_id', 'user_assigned_id'
        ]
    
    def validate_title(self, value):
        """Validate title is not empty."""
        if value and not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value.strip() if value else value
    
    def validate_amount(self, value):
        """Validate amount is positive."""
        if value is not None and value < 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value
    
    def validate_currency(self, value):
        """Validate currency code."""
        valid_currencies = ['USD', 'EUR', 'GBP', 'INR']
        if value not in valid_currencies:
            raise serializers.ValidationError(f"Currency must be one of: {', '.join(valid_currencies)}")
        return value
    
    def validate(self, attrs):
        """Cross-field validation."""
        # Validate person_id exists if provided
        person_id = attrs.get('person_id')
        if person_id:
            from apps.crm.models import Person
            if not Person.objects.filter(id=person_id, is_deleted=False).exists():
                raise serializers.ValidationError(
                    {"person_id": "Person with this ID does not exist."}
                )
        
        # Validate organisation_id exists if provided
        organisation_id = attrs.get('organisation_id')
        if organisation_id:
            from apps.crm.models import Organisation
            if not Organisation.objects.filter(id=organisation_id, is_deleted=False).exists():
                raise serializers.ValidationError(
                    {"organisation_id": "Organisation with this ID does not exist."}
                )
        
        # Validate lead_status_id exists if provided
        lead_status_id = attrs.get('lead_status_id')
        if lead_status_id:
            if not LeadStatus.objects.filter(id=lead_status_id, is_deleted=False).exists():
                raise serializers.ValidationError(
                    {"lead_status_id": "Lead status with this ID does not exist."}
                )
        
        # Validate lead_source_id exists if provided
        lead_source_id = attrs.get('lead_source_id')
        if lead_source_id:
            if not LeadSource.objects.filter(id=lead_source_id, is_deleted=False).exists():
                raise serializers.ValidationError(
                    {"lead_source_id": "Lead source with this ID does not exist."}
                )
        
        # Validate user_owner_id exists if provided
        user_owner_id = attrs.get('user_owner_id')
        if user_owner_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if not User.objects.filter(id=user_owner_id).exists():
                raise serializers.ValidationError(
                    {"user_owner_id": "User with this ID does not exist."}
                )
        
        # Validate user_assigned_id exists if provided
        user_assigned_id = attrs.get('user_assigned_id')
        if user_assigned_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if not User.objects.filter(id=user_assigned_id).exists():
                raise serializers.ValidationError(
                    {"user_assigned_id": "User with this ID does not exist."}
                )
        
        return attrs
    
    def update(self, instance, validated_data):
        """Update lead with user tracking."""
        user = self.context['request'].user
        validated_data['user_updated_id'] = user.id
        
        return super().update(instance, validated_data)


class LeadConvertSerializer(serializers.Serializer):
    """Serializer for converting lead to deal."""
    name = serializers.CharField(required=False, allow_blank=True)
    amount = serializers.DecimalField(required=False, allow_null=True, max_digits=10, decimal_places=2)
    
    def validate(self, attrs):
        """Validate lead can be converted."""
        lead = self.context['lead']
        
        if lead.converted_at:
            raise serializers.ValidationError("Lead has already been converted.")
        
        return attrs
