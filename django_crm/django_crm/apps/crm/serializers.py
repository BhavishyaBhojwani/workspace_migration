"""
CRM Serializers.
Response format matches Laravel's JSON structure for frontend compatibility.
"""
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType

from .models import (
    Organisation, Person, Email, Phone, Address, Label, Labelable,
    OrganisationType, Industry, Timezone, AddressType
)


# ========================
# NESTED SERIALIZERS
# ========================

class EmailSerializer(serializers.ModelSerializer):
    """Serializer for emails."""
    class Meta:
        model = Email
        fields = ['id', 'external_id', 'address', 'type', 'primary', 'created_at', 'updated_at']
        read_only_fields = ['id', 'external_id', 'created_at', 'updated_at']


class EmailInputSerializer(serializers.Serializer):
    """Input serializer for emails in create/update."""
    id = serializers.IntegerField(required=False, allow_null=True)
    address = serializers.EmailField(required=False, allow_blank=True)
    type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    primary = serializers.BooleanField(required=False, default=False)


class PhoneSerializer(serializers.ModelSerializer):
    """Serializer for phones."""
    class Meta:
        model = Phone
        fields = ['id', 'external_id', 'number', 'type', 'primary', 'created_at', 'updated_at']
        read_only_fields = ['id', 'external_id', 'created_at', 'updated_at']


class PhoneInputSerializer(serializers.Serializer):
    """Input serializer for phones in create/update."""
    id = serializers.IntegerField(required=False, allow_null=True)
    number = serializers.CharField(required=False, allow_blank=True)
    type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    primary = serializers.BooleanField(required=False, default=False)


class AddressTypeSerializer(serializers.ModelSerializer):
    """Serializer for address types."""
    class Meta:
        model = AddressType
        fields = ['id', 'name', 'created_at']


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for addresses."""
    address_type = AddressTypeSerializer(read_only=True)
    
    class Meta:
        model = Address
        fields = [
            'id', 'external_id', 'address_type_id', 'address_type',
            'address', 'name', 'contact', 'phone',
            'line1', 'line2', 'line3', 'city', 'state', 'code', 'country',
            'primary', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'external_id', 'address_type', 'created_at', 'updated_at']


class AddressInputSerializer(serializers.Serializer):
    """Input serializer for addresses in create/update."""
    id = serializers.IntegerField(required=False, allow_null=True)
    type = serializers.IntegerField(required=False, allow_null=True)
    address_type_id = serializers.IntegerField(required=False, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    contact = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    line1 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    line2 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    line3 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    state = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    country = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    primary = serializers.BooleanField(required=False, default=False)


class LabelSerializer(serializers.ModelSerializer):
    """Serializer for labels."""
    class Meta:
        model = Label
        fields = ['id', 'name', 'hex', 'color', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class OrganisationTypeSerializer(serializers.ModelSerializer):
    """Serializer for organisation types."""
    class Meta:
        model = OrganisationType
        fields = ['id', 'name', 'description', 'created_at']


class IndustrySerializer(serializers.ModelSerializer):
    """Serializer for industries."""
    class Meta:
        model = Industry
        fields = ['id', 'name', 'description', 'created_at']


class TimezoneSerializer(serializers.ModelSerializer):
    """Serializer for timezones."""
    class Meta:
        model = Timezone
        fields = ['id', 'name', 'offset', 'diff_from_gtm']


class UserMiniSerializer(serializers.Serializer):
    """Minimal user serializer for nested relations."""
    id = serializers.IntegerField()
    name = serializers.CharField()
    email = serializers.EmailField()


# ========================
# ORGANISATION SERIALIZERS
# ========================

class OrganisationListSerializer(serializers.ModelSerializer):
    """
    Serializer for organisation list view.
    Matches Laravel's index response format.
    """
    organisation_type = OrganisationTypeSerializer(read_only=True)
    industry = IndustrySerializer(read_only=True)
    user_owner = UserMiniSerializer(read_only=True)
    labels = serializers.SerializerMethodField()
    primary_email = serializers.SerializerMethodField()
    primary_phone = serializers.SerializerMethodField()
    primary_address = serializers.SerializerMethodField()
    people_count = serializers.SerializerMethodField()
    deals_count = serializers.SerializerMethodField()
    
    # Convert cents to currency for display
    annual_revenue_display = serializers.SerializerMethodField()
    total_money_raised_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Organisation
        fields = [
            'id', 'external_id', 'name', 'description',
            'organisation_type_id', 'organisation_type',
            'industry_id', 'industry',
            'timezone_id',
            'vat_number', 'number_of_employees',
            'annual_revenue', 'annual_revenue_display',
            'total_money_raised', 'total_money_raised_display',
            'linkedin',
            'user_owner_id', 'user_owner',
            'labels',
            'primary_email', 'primary_phone', 'primary_address',
            'people_count', 'deals_count',
            'created_at', 'updated_at',
        ]
    
    def get_labels(self, obj):
        labels = []
        for labelable in obj.labelables.all():
            if labelable.label:
                labels.append(LabelSerializer(labelable.label).data)
        return labels
    
    def get_primary_email(self, obj):
        email = obj.emails.filter(primary=True).first()
        if not email:
            email = obj.emails.first()
        return EmailSerializer(email).data if email else None
    
    def get_primary_phone(self, obj):
        phone = obj.phones.filter(primary=True).first()
        if not phone:
            phone = obj.phones.first()
        return PhoneSerializer(phone).data if phone else None
    
    def get_primary_address(self, obj):
        address = obj.addresses.filter(primary=True).first()
        if not address:
            address = obj.addresses.first()
        return AddressSerializer(address).data if address else None
    
    def get_people_count(self, obj):
        try:
            return obj.people.filter(is_deleted=False).count() if hasattr(obj, 'people') else 0
        except Exception:
            return 0
    
    def get_deals_count(self, obj):
        try:
            return obj.deals.filter(is_deleted=False).count() if hasattr(obj, 'deals') else 0
        except Exception:
            return 0
    
    def get_annual_revenue_display(self, obj):
        if obj.annual_revenue:
            return obj.annual_revenue / 100
        return None
    
    def get_total_money_raised_display(self, obj):
        if obj.total_money_raised:
            return obj.total_money_raised / 100
        return None


class OrganisationDetailSerializer(OrganisationListSerializer):
    """
    Serializer for organisation detail view.
    Includes all related data.
    """
    emails = EmailSerializer(many=True, read_only=True)
    phones = PhoneSerializer(many=True, read_only=True)
    addresses = AddressSerializer(many=True, read_only=True)
    timezone = TimezoneSerializer(read_only=True)
    user_created = UserMiniSerializer(read_only=True)
    
    class Meta(OrganisationListSerializer.Meta):
        fields = OrganisationListSerializer.Meta.fields + [
            'emails', 'phones', 'addresses', 'timezone', 'user_created',
        ]


class OrganisationCreateSerializer(serializers.Serializer):
    """
    Serializer for creating organisations.
    Matches Laravel's StoreOrganisationRequest validation.
    """
    name = serializers.CharField(max_length=1000, required=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    organisation_type_id = serializers.IntegerField(required=False, allow_null=True)
    industry_id = serializers.IntegerField(required=False, allow_null=True)
    timezone_id = serializers.IntegerField(required=False, allow_null=True)
    vat_number = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    number_of_employees = serializers.IntegerField(required=False, allow_null=True)
    annual_revenue = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    total_money_raised = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    linkedin = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    user_owner_id = serializers.IntegerField(required=False, allow_null=True)
    
    # Nested data
    emails = EmailInputSerializer(many=True, required=False)
    phones = PhoneInputSerializer(many=True, required=False)
    addresses = AddressInputSerializer(many=True, required=False)
    labels = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    
    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Name is required.")
        return value.strip()


class OrganisationUpdateSerializer(OrganisationCreateSerializer):
    """
    Serializer for updating organisations.
    Matches Laravel's UpdateOrganisationRequest validation.
    """
    name = serializers.CharField(max_length=1000, required=False)


# ========================
# PERSON SERIALIZERS
# ========================

class PersonListSerializer(serializers.ModelSerializer):
    """Serializer for person list view."""
    organisation = serializers.SerializerMethodField()
    user_owner = UserMiniSerializer(read_only=True)
    labels = serializers.SerializerMethodField()
    primary_email = serializers.SerializerMethodField()
    primary_phone = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Person
        fields = [
            'id', 'external_id', 'title', 'first_name', 'middle_name', 'last_name',
            'full_name', 'birthday', 'gender', 'description',
            'organisation_id', 'organisation',
            'user_owner_id', 'user_owner',
            'labels',
            'primary_email', 'primary_phone',
            'created_at', 'updated_at',
        ]
    
    def get_organisation(self, obj):
        if obj.organisation:
            return {
                'id': obj.organisation.id,
                'name': obj.organisation.name,
            }
        return None
    
    def get_labels(self, obj):
        labels = []
        for labelable in obj.labelables.all():
            if labelable.label:
                labels.append(LabelSerializer(labelable.label).data)
        return labels
    
    def get_primary_email(self, obj):
        email = obj.emails.filter(primary=True).first()
        if not email:
            email = obj.emails.first()
        return EmailSerializer(email).data if email else None
    
    def get_primary_phone(self, obj):
        phone = obj.phones.filter(primary=True).first()
        if not phone:
            phone = obj.phones.first()
        return PhoneSerializer(phone).data if phone else None
    
    def get_full_name(self, obj):
        parts = [obj.title, obj.first_name, obj.middle_name, obj.last_name]
        return ' '.join(filter(None, parts))


class PersonDetailSerializer(PersonListSerializer):
    """Serializer for person detail view."""
    emails = EmailSerializer(many=True, read_only=True)
    phones = PhoneSerializer(many=True, read_only=True)
    addresses = AddressSerializer(many=True, read_only=True)
    user_created = UserMiniSerializer(read_only=True)
    
    class Meta(PersonListSerializer.Meta):
        fields = PersonListSerializer.Meta.fields + [
            'maiden_name', 'emails', 'phones', 'addresses', 'user_created',
        ]


class PersonCreateSerializer(serializers.Serializer):
    """Serializer for creating persons."""
    title = serializers.CharField(max_length=500, required=False, allow_blank=True, allow_null=True)
    first_name = serializers.CharField(max_length=500, required=True)
    middle_name = serializers.CharField(max_length=500, required=False, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(max_length=500, required=False, allow_blank=True, allow_null=True)
    maiden_name = serializers.CharField(max_length=500, required=False, allow_blank=True, allow_null=True)
    birthday = serializers.DateField(required=False, allow_null=True)
    gender = serializers.ChoiceField(choices=['male', 'female'], required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    organisation_id = serializers.IntegerField(required=False, allow_null=True)
    user_owner_id = serializers.IntegerField(required=False, allow_null=True)
    
    emails = EmailInputSerializer(many=True, required=False)
    phones = PhoneInputSerializer(many=True, required=False)
    addresses = AddressInputSerializer(many=True, required=False)
    labels = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )


class PersonUpdateSerializer(PersonCreateSerializer):
    """Serializer for updating persons."""
    first_name = serializers.CharField(max_length=500, required=False)


# ========================
# LEAD, PIPELINE & DEAL SERIALIZERS
# ========================

from apps.pipeline.models import (
    LeadStatus, LeadSource, Pipeline, PipelineStage,
    PipelineStageProbability, Lead, Deal, DealProduct
)


class LeadStatusSerializer(serializers.ModelSerializer):
    """Serializer for lead statuses."""
    class Meta:
        model = LeadStatus
        fields = ['id', 'external_id', 'name', 'description', 'order', 'created_at', 'updated_at']
        read_only_fields = ['id', 'external_id', 'created_at', 'updated_at']


class LeadSourceSerializer(serializers.ModelSerializer):
    """Serializer for lead sources."""
    class Meta:
        model = LeadSource
        fields = ['id', 'external_id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'external_id', 'created_at', 'updated_at']


class PipelineStageProbabilitySerializer(serializers.ModelSerializer):
    """Serializer for pipeline stage probabilities."""
    class Meta:
        model = PipelineStageProbability
        fields = ['id', 'external_id', 'name', 'percent', 'created_at', 'updated_at']
        read_only_fields = ['id', 'external_id', 'created_at', 'updated_at']


class PipelineStageSerializer(serializers.ModelSerializer):
    """Serializer for pipeline stages."""
    pipeline_stage_probability = PipelineStageProbabilitySerializer(read_only=True)
    
    class Meta:
        model = PipelineStage
        fields = [
            'id', 'external_id', 'pipeline_id', 'name', 'description',
            'pipeline_stage_probability', 'order', 'color', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'external_id', 'created_at', 'updated_at']


class PipelineSerializer(serializers.ModelSerializer):
    """Serializer for pipelines."""
    stages = PipelineStageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Pipeline
        fields = ['id', 'external_id', 'name', 'model', 'stages', 'created_at', 'updated_at']
        read_only_fields = ['id', 'external_id', 'created_at', 'updated_at']


class PipelineListSerializer(serializers.ModelSerializer):
    """List serializer for pipelines (without nested stages)."""
    stages_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Pipeline
        fields = ['id', 'external_id', 'name', 'model', 'stages_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'external_id', 'created_at', 'updated_at']
    
    def get_stages_count(self, obj):
        return obj.stages.filter(is_deleted=False).count()


class DealProductSerializer(serializers.ModelSerializer):
    """Serializer for deal products."""
    product_name = serializers.SerializerMethodField()
    price_display = serializers.SerializerMethodField()
    amount_display = serializers.SerializerMethodField()
    
    class Meta:
        model = DealProduct
        fields = [
            'id', 'external_id', 'deal_id', 'product_id', 'product_name',
            'price', 'price_display', 'quantity', 'amount', 'amount_display',
            'tax_rate', 'tax_amount', 'currency', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'external_id', 'created_at', 'updated_at']
    
    def get_product_name(self, obj):
        return obj.product.name if obj.product else None
    
    def get_price_display(self, obj):
        if obj.price:
            return obj.price / 100
        return None
    
    def get_amount_display(self, obj):
        if obj.amount:
            return obj.amount / 100
        return None


class LeadSerializer(serializers.ModelSerializer):
    """Full serializer for leads."""
    lead_status = LeadStatusSerializer(read_only=True)
    lead_source = LeadSourceSerializer(read_only=True)
    pipeline_stage = PipelineStageSerializer(read_only=True)
    person = PersonListSerializer(read_only=True)
    organisation = OrganisationListSerializer(read_only=True)
    amount_display = serializers.SerializerMethodField()
    primary_email = serializers.SerializerMethodField()
    primary_phone = serializers.SerializerMethodField()
    
    class Meta:
        model = Lead
        fields = [
            'id', 'external_id', 'lead_id', 'title', 'description',
            'amount', 'amount_display', 'currency', 'qualified',
            'expected_close', 'converted_at',
            'lead_status_id', 'lead_status',
            'lead_source_id', 'lead_source',
            'pipeline_id', 'pipeline_stage_id', 'pipeline_stage',
            'person_id', 'person', 'organisation_id', 'organisation',
            'user_owner_id', 'user_assigned_id',
            'primary_email', 'primary_phone',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'external_id', 'lead_id', 'created_at', 'updated_at']
    
    def get_amount_display(self, obj):
        if obj.amount:
            return obj.amount / 100
        return None
    
    def get_primary_email(self, obj):
        # Get email from person
        if obj.person:
            email = obj.person.emails.filter(primary=True).first()
            if not email:
                email = obj.person.emails.first()
            if email:
                return email.address
        return None
    
    def get_primary_phone(self, obj):
        if obj.person:
            phone = obj.person.phones.filter(primary=True).first()
            if not phone:
                phone = obj.person.phones.first()
            if phone:
                return phone.number
        return None


class LeadListSerializer(serializers.ModelSerializer):
    """List serializer for leads (lightweight)."""
    lead_status_name = serializers.SerializerMethodField()
    pipeline_stage_name = serializers.SerializerMethodField()
    person_name = serializers.SerializerMethodField()
    organisation_name = serializers.SerializerMethodField()
    amount_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Lead
        fields = [
            'id', 'external_id', 'lead_id', 'title',
            'amount', 'amount_display', 'currency',
            'lead_status_name', 'pipeline_stage_name',
            'person_id', 'person_name', 
            'organisation_id', 'organisation_name',
            'expected_close', 'converted_at', 'created_at'
        ]
        read_only_fields = ['id', 'external_id', 'lead_id', 'created_at']
    
    def get_lead_status_name(self, obj):
        return obj.lead_status.name if obj.lead_status else None
    
    def get_pipeline_stage_name(self, obj):
        return obj.pipeline_stage.name if obj.pipeline_stage else None
    
    def get_person_name(self, obj):
        if obj.person:
            return f"{obj.person.first_name} {obj.person.last_name or ''}".strip()
        return None
    
    def get_organisation_name(self, obj):
        return obj.organisation.name if obj.organisation else None
    
    def get_amount_display(self, obj):
        if obj.amount:
            return obj.amount / 100
        return None


class LeadCreateSerializer(serializers.Serializer):
    """Serializer for creating leads."""
    title = serializers.CharField(max_length=255, required=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    currency = serializers.CharField(max_length=3, required=False, default='USD')
    qualified = serializers.BooleanField(required=False, default=False)
    expected_close = serializers.DateTimeField(required=False, allow_null=True)
    
    person_id = serializers.IntegerField(required=False, allow_null=True)
    organisation_id = serializers.IntegerField(required=False, allow_null=True)
    lead_status_id = serializers.IntegerField(required=False, allow_null=True)
    lead_source_id = serializers.IntegerField(required=False, allow_null=True)
    pipeline_stage_id = serializers.IntegerField(required=False, allow_null=True)
    user_owner_id = serializers.IntegerField(required=False, allow_null=True)
    user_assigned_id = serializers.IntegerField(required=False, allow_null=True)
    
    labels = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )


class LeadUpdateSerializer(LeadCreateSerializer):
    """Serializer for updating leads."""
    title = serializers.CharField(max_length=255, required=False)


class LeadConvertSerializer(serializers.Serializer):
    """Serializer for converting lead to deal."""
    title = serializers.CharField(max_length=255, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    currency = serializers.CharField(max_length=3, required=False)
    pipeline_stage_id = serializers.IntegerField(required=False, allow_null=True)
    expected_close = serializers.DateTimeField(required=False, allow_null=True)
    person_id = serializers.IntegerField(required=False, allow_null=True)
    organisation_id = serializers.IntegerField(required=False, allow_null=True)
    user_owner_id = serializers.IntegerField(required=False, allow_null=True)
    user_assigned_id = serializers.IntegerField(required=False, allow_null=True)
    labels = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )


class DealSerializer(serializers.ModelSerializer):
    """Full serializer for deals."""
    pipeline_stage = PipelineStageSerializer(read_only=True)
    person = PersonListSerializer(read_only=True)
    organisation = OrganisationListSerializer(read_only=True)
    deal_products = DealProductSerializer(many=True, read_only=True)
    amount_display = serializers.SerializerMethodField()
    primary_email = serializers.SerializerMethodField()
    primary_phone = serializers.SerializerMethodField()
    
    class Meta:
        model = Deal
        fields = [
            'id', 'external_id', 'deal_id', 'title', 'description',
            'amount', 'amount_display', 'currency', 'qualified',
            'expected_close', 'closed_at', 'closed_status',
            'pipeline_id', 'pipeline_stage_id', 'pipeline_stage',
            'person_id', 'person', 'organisation_id', 'organisation',
            'lead_id', 'deal_products',
            'user_owner_id', 'user_assigned_id',
            'primary_email', 'primary_phone',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'external_id', 'deal_id', 'created_at', 'updated_at']
    
    def get_amount_display(self, obj):
        if obj.amount:
            return obj.amount / 100
        return None
    
    def get_primary_email(self, obj):
        if obj.person:
            email = obj.person.emails.filter(primary=True).first()
            if not email:
                email = obj.person.emails.first()
            if email:
                return email.address
        return None
    
    def get_primary_phone(self, obj):
        if obj.person:
            phone = obj.person.phones.filter(primary=True).first()
            if not phone:
                phone = obj.person.phones.first()
            if phone:
                return phone.number
        return None


class DealListSerializer(serializers.ModelSerializer):
    """List serializer for deals (lightweight)."""
    pipeline_stage_name = serializers.SerializerMethodField()
    person_name = serializers.SerializerMethodField()
    organisation_name = serializers.SerializerMethodField()
    amount_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Deal
        fields = [
            'id', 'external_id', 'deal_id', 'title',
            'amount', 'amount_display', 'currency',
            'pipeline_stage_name', 'closed_status',
            'person_id', 'person_name',
            'organisation_id', 'organisation_name',
            'expected_close', 'closed_at', 'created_at'
        ]
        read_only_fields = ['id', 'external_id', 'deal_id', 'created_at']
    
    def get_pipeline_stage_name(self, obj):
        return obj.pipeline_stage.name if obj.pipeline_stage else None
    
    def get_person_name(self, obj):
        if obj.person:
            return f"{obj.person.first_name} {obj.person.last_name or ''}".strip()
        return None
    
    def get_organisation_name(self, obj):
        return obj.organisation.name if obj.organisation else None
    
    def get_amount_display(self, obj):
        if obj.amount:
            return obj.amount / 100
        return None


class DealProductInputSerializer(serializers.Serializer):
    """Input serializer for deal products in create/update."""
    id = serializers.IntegerField(required=False, allow_null=True)
    product_id = serializers.IntegerField(required=False, allow_null=True)
    price = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    quantity = serializers.IntegerField(required=False, default=1)
    comments = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class DealCreateSerializer(serializers.Serializer):
    """Serializer for creating deals."""
    title = serializers.CharField(max_length=255, required=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    currency = serializers.CharField(max_length=3, required=False, default='USD')
    qualified = serializers.BooleanField(required=False, default=False)
    expected_close = serializers.DateTimeField(required=False, allow_null=True)
    
    person_id = serializers.IntegerField(required=False, allow_null=True)
    organisation_id = serializers.IntegerField(required=False, allow_null=True)
    pipeline_stage_id = serializers.IntegerField(required=False, allow_null=True)
    user_owner_id = serializers.IntegerField(required=False, allow_null=True)
    user_assigned_id = serializers.IntegerField(required=False, allow_null=True)
    
    products = DealProductInputSerializer(many=True, required=False)
    labels = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )


class DealUpdateSerializer(DealCreateSerializer):
    """Serializer for updating deals."""
    title = serializers.CharField(max_length=255, required=False)


class DealCloseSerializer(serializers.Serializer):
    """Serializer for closing deals."""
    status = serializers.ChoiceField(choices=['won', 'lost'], required=True)
    closed_at = serializers.DateTimeField(required=False, allow_null=True)


class PipelineCreateSerializer(serializers.Serializer):
    """Serializer for creating pipelines."""
    name = serializers.CharField(max_length=255, required=True)
    model = serializers.ChoiceField(choices=['Lead', 'Deal', 'Quote'], required=False, default='Deal')


class PipelineUpdateSerializer(serializers.Serializer):
    """Serializer for updating pipelines."""
    name = serializers.CharField(max_length=255, required=False)
    model = serializers.ChoiceField(choices=['Lead', 'Deal', 'Quote'], required=False)


class PipelineStageCreateSerializer(serializers.Serializer):
    """Serializer for creating pipeline stages."""
    pipeline_id = serializers.IntegerField(required=True)
    probability_id = serializers.IntegerField(required=False, allow_null=True)
    name = serializers.CharField(max_length=255, required=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    order = serializers.IntegerField(required=False, default=0)
    color = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)


class PipelineStageUpdateSerializer(serializers.Serializer):
    """Serializer for updating pipeline stages."""
    probability_id = serializers.IntegerField(required=False, allow_null=True)
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    order = serializers.IntegerField(required=False)
    color = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
