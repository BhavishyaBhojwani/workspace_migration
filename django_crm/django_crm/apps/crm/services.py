"""
Services for CRM models - business logic separated from views.
Replicates Laravel's Service classes.
"""
import uuid
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from .models import (
    Organisation, Person, Email, Phone, Address, Labelable, Contact
)


class OrganisationService:
    """
    Service for organisation business logic.
    Replicates Laravel's OrganisationService.
    """
    
    @staticmethod
    @transaction.atomic
    def create(user, data):
        """
        Create a new organisation.
        Replicates Laravel's OrganisationService::create().
        """
        # Create organisation
        organisation = Organisation.objects.create(
            external_id=str(uuid.uuid4()),
            team_id=user.current_crm_team.id if user.current_crm_team else None,
            name=data.get('name'),
            description=data.get('description'),
            organisation_type_id=data.get('organisation_type_id'),
            industry_id=data.get('industry_id'),
            timezone_id=data.get('timezone_id'),
            vat_number=data.get('vat_number'),
            number_of_employees=data.get('number_of_employees'),
            annual_revenue=OrganisationService._convert_to_cents(data.get('annual_revenue')),
            total_money_raised=OrganisationService._convert_to_cents(data.get('total_money_raised')),
            linkedin=data.get('linkedin'),
            user_owner_id=data.get('user_owner_id'),
            user_created=user,
        )
        
        # Handle related data
        OrganisationService._update_phones(organisation, data.get('phones', []))
        OrganisationService._update_emails(organisation, data.get('emails', []))
        OrganisationService._update_addresses(organisation, data.get('addresses', []))
        OrganisationService._sync_labels(organisation, data.get('labels', []))
        
        return organisation
    
    @staticmethod
    @transaction.atomic
    def update(organisation, user, data):
        """
        Update an organisation.
        Replicates Laravel's OrganisationService::update().
        """
        organisation.name = data.get('name', organisation.name)
        organisation.description = data.get('description', organisation.description)
        organisation.organisation_type_id = data.get('organisation_type_id', organisation.organisation_type_id)
        organisation.industry_id = data.get('industry_id', organisation.industry_id)
        organisation.timezone_id = data.get('timezone_id', organisation.timezone_id)
        organisation.vat_number = data.get('vat_number', organisation.vat_number)
        organisation.number_of_employees = data.get('number_of_employees', organisation.number_of_employees)
        
        if 'annual_revenue' in data:
            organisation.annual_revenue = OrganisationService._convert_to_cents(data.get('annual_revenue'))
        if 'total_money_raised' in data:
            organisation.total_money_raised = OrganisationService._convert_to_cents(data.get('total_money_raised'))
        
        organisation.linkedin = data.get('linkedin', organisation.linkedin)
        organisation.user_owner_id = data.get('user_owner_id', organisation.user_owner_id)
        organisation.user_updated = user
        organisation.save()
        
        # Handle related data
        if 'phones' in data:
            OrganisationService._update_phones(organisation, data.get('phones', []))
        if 'emails' in data:
            OrganisationService._update_emails(organisation, data.get('emails', []))
        if 'addresses' in data:
            OrganisationService._update_addresses(organisation, data.get('addresses', []))
        if 'labels' in data:
            OrganisationService._sync_labels(organisation, data.get('labels', []))
        
        return organisation
    
    @staticmethod
    @transaction.atomic
    def delete(organisation, user):
        """
        Soft delete an organisation.
        Replicates Laravel's OrganisationController::destroy().
        """
        # Delete related contacts first
        content_type = ContentType.objects.get_for_model(Organisation)
        Contact.objects.filter(
            entityable_type=content_type,
            entityable_id=organisation.id
        ).delete()
        
        # Soft delete organisation
        organisation.is_deleted = True
        organisation.deleted_at = timezone.now()
        organisation.user_deleted = user
        organisation.save()
        
        return True
    
    @staticmethod
    def restore(organisation, user):
        """Restore a soft-deleted organisation."""
        organisation.is_deleted = False
        organisation.deleted_at = None
        organisation.user_restored = user
        organisation.save()
        return organisation
    
    @staticmethod
    def _convert_to_cents(value):
        """
        Convert currency value to cents (multiply by 100).
        Replicates Laravel's attribute mutators.
        """
        if value is None:
            return None
        return int(float(value) * 100)
    
    @staticmethod
    def _update_phones(organisation, phones):
        """
        Update organisation phones.
        Replicates Laravel's OrganisationService::updateOrganisationPhones().
        """
        content_type = ContentType.objects.get_for_model(Organisation)
        phone_ids = []
        
        for phone_data in phones or []:
            phone_id = phone_data.get('id')
            number = phone_data.get('number')
            
            if not number:
                continue
            
            if phone_id:
                # Update existing phone
                try:
                    phone = Phone.objects.get(id=phone_id)
                    phone.number = number
                    phone.type = phone_data.get('type')
                    phone.primary = phone_data.get('primary') in [True, 'on', 1, '1']
                    phone.save()
                    phone_ids.append(phone.id)
                except Phone.DoesNotExist:
                    pass
            else:
                # Create new phone
                phone = Phone.objects.create(
                    external_id=str(uuid.uuid4()),
                    phoneable_type=content_type,
                    phoneable_id=organisation.id,
                    number=number,
                    type=phone_data.get('type'),
                    primary=phone_data.get('primary') in [True, 'on', 1, '1'],
                )
                phone_ids.append(phone.id)
        
        # Delete phones not in the list
        organisation.phones.exclude(id__in=phone_ids).delete()
    
    @staticmethod
    def _update_emails(organisation, emails):
        """
        Update organisation emails.
        Replicates Laravel's OrganisationService::updateOrganisationEmails().
        """
        content_type = ContentType.objects.get_for_model(Organisation)
        email_ids = []
        
        for email_data in emails or []:
            email_id = email_data.get('id')
            address = email_data.get('address')
            
            if not address:
                continue
            
            if email_id:
                try:
                    email = Email.objects.get(id=email_id)
                    email.address = address
                    email.type = email_data.get('type')
                    email.primary = email_data.get('primary') in [True, 'on', 1, '1']
                    email.save()
                    email_ids.append(email.id)
                except Email.DoesNotExist:
                    pass
            else:
                email = Email.objects.create(
                    external_id=str(uuid.uuid4()),
                    emailable_type=content_type,
                    emailable_id=organisation.id,
                    address=address,
                    type=email_data.get('type'),
                    primary=email_data.get('primary') in [True, 'on', 1, '1'],
                )
                email_ids.append(email.id)
        
        organisation.emails.exclude(id__in=email_ids).delete()
    
    @staticmethod
    def _update_addresses(organisation, addresses):
        """
        Update organisation addresses.
        Replicates Laravel's OrganisationService::updateOrganisationAddresses().
        """
        content_type = ContentType.objects.get_for_model(Organisation)
        address_ids = []
        
        for addr_data in addresses or []:
            addr_id = addr_data.get('id')
            
            if addr_id:
                try:
                    address = Address.objects.get(id=addr_id)
                    address.address_type_id = addr_data.get('type') or addr_data.get('address_type_id')
                    address.address = addr_data.get('address')
                    address.name = addr_data.get('name')
                    address.contact = addr_data.get('contact')
                    address.phone = addr_data.get('phone')
                    address.line1 = addr_data.get('line1')
                    address.line2 = addr_data.get('line2')
                    address.line3 = addr_data.get('line3')
                    address.city = addr_data.get('city')
                    address.state = addr_data.get('state')
                    address.code = addr_data.get('code')
                    address.country = addr_data.get('country')
                    address.primary = addr_data.get('primary') in [True, 'on', 1, '1']
                    address.save()
                    address_ids.append(address.id)
                except Address.DoesNotExist:
                    pass
            else:
                address = Address.objects.create(
                    external_id=str(uuid.uuid4()),
                    addressable_type=content_type,
                    addressable_id=organisation.id,
                    address_type_id=addr_data.get('type') or addr_data.get('address_type_id'),
                    address=addr_data.get('address'),
                    name=addr_data.get('name'),
                    contact=addr_data.get('contact'),
                    phone=addr_data.get('phone'),
                    line1=addr_data.get('line1'),
                    line2=addr_data.get('line2'),
                    line3=addr_data.get('line3'),
                    city=addr_data.get('city'),
                    state=addr_data.get('state'),
                    code=addr_data.get('code'),
                    country=addr_data.get('country'),
                    primary=addr_data.get('primary') in [True, 'on', 1, '1'],
                )
                address_ids.append(address.id)
        
        organisation.addresses.exclude(id__in=address_ids).delete()
    
    @staticmethod
    def _sync_labels(organisation, label_ids):
        """
        Sync organisation labels.
        Replicates Laravel's $organisation->labels()->sync().
        """
        content_type = ContentType.objects.get_for_model(Organisation)
        
        # Remove old labels
        Labelable.objects.filter(
            labelable_type=content_type,
            labelable_id=organisation.id
        ).delete()
        
        # Add new labels
        for label_id in label_ids or []:
            Labelable.objects.create(
                label_id=label_id,
                labelable_type=content_type,
                labelable_id=organisation.id
            )


class PersonService:
    """Service for person business logic."""
    
    @staticmethod
    @transaction.atomic
    def create(user, data):
        """Create a new person."""
        person = Person.objects.create(
            external_id=str(uuid.uuid4()),
            team_id=user.current_crm_team.id if user.current_crm_team else None,
            title=data.get('title'),
            first_name=data.get('first_name'),
            middle_name=data.get('middle_name'),
            last_name=data.get('last_name'),
            maiden_name=data.get('maiden_name'),
            birthday=data.get('birthday'),
            gender=data.get('gender'),
            description=data.get('description'),
            organisation_id=data.get('organisation_id'),
            user_owner_id=data.get('user_owner_id'),
            user_created=user,
        )
        
        PersonService._update_phones(person, data.get('phones', []))
        PersonService._update_emails(person, data.get('emails', []))
        PersonService._update_addresses(person, data.get('addresses', []))
        PersonService._sync_labels(person, data.get('labels', []))
        
        return person
    
    @staticmethod
    @transaction.atomic
    def update(person, user, data):
        """Update a person."""
        person.title = data.get('title', person.title)
        person.first_name = data.get('first_name', person.first_name)
        person.middle_name = data.get('middle_name', person.middle_name)
        person.last_name = data.get('last_name', person.last_name)
        person.maiden_name = data.get('maiden_name', person.maiden_name)
        person.birthday = data.get('birthday', person.birthday)
        person.gender = data.get('gender', person.gender)
        person.description = data.get('description', person.description)
        person.organisation_id = data.get('organisation_id', person.organisation_id)
        person.user_owner_id = data.get('user_owner_id', person.user_owner_id)
        person.user_updated = user
        person.save()
        
        if 'phones' in data:
            PersonService._update_phones(person, data.get('phones', []))
        if 'emails' in data:
            PersonService._update_emails(person, data.get('emails', []))
        if 'addresses' in data:
            PersonService._update_addresses(person, data.get('addresses', []))
        if 'labels' in data:
            PersonService._sync_labels(person, data.get('labels', []))
        
        return person
    
    @staticmethod
    @transaction.atomic
    def delete(person, user):
        """Soft delete a person."""
        person.is_deleted = True
        person.deleted_at = timezone.now()
        person.user_deleted = user
        person.save()
        return True
    
    @staticmethod
    def _update_phones(person, phones):
        """Update person phones."""
        content_type = ContentType.objects.get_for_model(Person)
        phone_ids = []
        
        for phone_data in phones or []:
            phone_id = phone_data.get('id')
            number = phone_data.get('number')
            
            if not number:
                continue
            
            if phone_id:
                try:
                    phone = Phone.objects.get(id=phone_id)
                    phone.number = number
                    phone.type = phone_data.get('type')
                    phone.primary = phone_data.get('primary') in [True, 'on', 1, '1']
                    phone.save()
                    phone_ids.append(phone.id)
                except Phone.DoesNotExist:
                    pass
            else:
                phone = Phone.objects.create(
                    external_id=str(uuid.uuid4()),
                    phoneable_type=content_type,
                    phoneable_id=person.id,
                    number=number,
                    type=phone_data.get('type'),
                    primary=phone_data.get('primary') in [True, 'on', 1, '1'],
                )
                phone_ids.append(phone.id)
        
        person.phones.exclude(id__in=phone_ids).delete()
    
    @staticmethod
    def _update_emails(person, emails):
        """Update person emails."""
        content_type = ContentType.objects.get_for_model(Person)
        email_ids = []
        
        for email_data in emails or []:
            email_id = email_data.get('id')
            address = email_data.get('address')
            
            if not address:
                continue
            
            if email_id:
                try:
                    email = Email.objects.get(id=email_id)
                    email.address = address
                    email.type = email_data.get('type')
                    email.primary = email_data.get('primary') in [True, 'on', 1, '1']
                    email.save()
                    email_ids.append(email.id)
                except Email.DoesNotExist:
                    pass
            else:
                email = Email.objects.create(
                    external_id=str(uuid.uuid4()),
                    emailable_type=content_type,
                    emailable_id=person.id,
                    address=address,
                    type=email_data.get('type'),
                    primary=email_data.get('primary') in [True, 'on', 1, '1'],
                )
                email_ids.append(email.id)
        
        person.emails.exclude(id__in=email_ids).delete()
    
    @staticmethod
    def _update_addresses(person, addresses):
        """Update person addresses."""
        content_type = ContentType.objects.get_for_model(Person)
        address_ids = []
        
        for addr_data in addresses or []:
            addr_id = addr_data.get('id')
            
            if addr_id:
                try:
                    address = Address.objects.get(id=addr_id)
                    address.address_type_id = addr_data.get('type') or addr_data.get('address_type_id')
                    address.line1 = addr_data.get('line1')
                    address.line2 = addr_data.get('line2')
                    address.line3 = addr_data.get('line3')
                    address.city = addr_data.get('city')
                    address.state = addr_data.get('state')
                    address.code = addr_data.get('code')
                    address.country = addr_data.get('country')
                    address.primary = addr_data.get('primary') in [True, 'on', 1, '1']
                    address.save()
                    address_ids.append(address.id)
                except Address.DoesNotExist:
                    pass
            else:
                address = Address.objects.create(
                    external_id=str(uuid.uuid4()),
                    addressable_type=content_type,
                    addressable_id=person.id,
                    address_type_id=addr_data.get('type') or addr_data.get('address_type_id'),
                    line1=addr_data.get('line1'),
                    line2=addr_data.get('line2'),
                    line3=addr_data.get('line3'),
                    city=addr_data.get('city'),
                    state=addr_data.get('state'),
                    code=addr_data.get('code'),
                    country=addr_data.get('country'),
                    primary=addr_data.get('primary') in [True, 'on', 1, '1'],
                )
                address_ids.append(address.id)
        
        person.addresses.exclude(id__in=address_ids).delete()
    
    @staticmethod
    def _sync_labels(person, label_ids):
        """Sync person labels."""
        content_type = ContentType.objects.get_for_model(Person)
        
        Labelable.objects.filter(
            labelable_type=content_type,
            labelable_id=person.id
        ).delete()
        
        for label_id in label_ids or []:
            Labelable.objects.create(
                label_id=label_id,
                labelable_type=content_type,
                labelable_id=person.id
            )


# ============================================================================
# LEAD, PIPELINE & DEAL SERVICES
# ============================================================================

from apps.pipeline.models import (
    LeadStatus, LeadSource, Pipeline, PipelineStage, 
    PipelineStageProbability, Lead, Deal, DealProduct
)


class PipelineService:
    """Service for pipeline business logic."""
    
    @staticmethod
    @transaction.atomic
    def create(user, data):
        """Create a new pipeline."""
        pipeline = Pipeline.objects.create(
            external_id=str(uuid.uuid4()),
            team_id=user.current_crm_team.id if user.current_crm_team else None,
            name=data.get('name'),
            model=data.get('model', 'Deal'),
        )
        return pipeline
    
    @staticmethod
    @transaction.atomic
    def update(pipeline, user, data):
        """Update a pipeline."""
        pipeline.name = data.get('name', pipeline.name)
        pipeline.model = data.get('model', pipeline.model)
        pipeline.save()
        return pipeline
    
    @staticmethod
    @transaction.atomic
    def delete(pipeline, user):
        """Soft delete a pipeline."""
        pipeline.is_deleted = True
        pipeline.deleted_at = timezone.now()
        pipeline.save()
        return True
    
    @staticmethod
    def get_default_pipeline(model_type='Deal'):
        """Get the default pipeline for a model type."""
        return Pipeline.objects.filter(
            model=model_type, 
            is_deleted=False
        ).first()


class PipelineStageService:
    """Service for pipeline stage business logic."""
    
    @staticmethod
    @transaction.atomic
    def create(user, data):
        """Create a new pipeline stage."""
        stage = PipelineStage.objects.create(
            external_id=str(uuid.uuid4()),
            team_id=user.current_crm_team.id if user.current_crm_team else None,
            pipeline_id=data.get('pipeline_id'),
            probability_id=data.get('probability_id'),
            name=data.get('name'),
            description=data.get('description'),
            order=data.get('order', 0),
            color=data.get('color'),
        )
        return stage
    
    @staticmethod
    @transaction.atomic
    def update(stage, user, data):
        """Update a pipeline stage."""
        stage.name = data.get('name', stage.name)
        stage.description = data.get('description', stage.description)
        stage.order = data.get('order', stage.order)
        stage.color = data.get('color', stage.color)
        stage.probability_id = data.get('probability_id', stage.probability_id)
        stage.save()
        return stage
    
    @staticmethod
    @transaction.atomic
    def delete(stage, user):
        """Soft delete a pipeline stage."""
        stage.is_deleted = True
        stage.deleted_at = timezone.now()
        stage.save()
        return True


class LeadService:
    """
    Service for lead business logic.
    Replicates Laravel's LeadService.
    """
    
    @staticmethod
    @transaction.atomic
    def create(user, data, person=None, organisation=None, client=None):
        """
        Create a new lead.
        Replicates Laravel's LeadService::create().
        """
        # Get pipeline from pipeline_stage
        pipeline_id = None
        pipeline_stage_id = data.get('pipeline_stage_id')
        if pipeline_stage_id:
            try:
                stage = PipelineStage.objects.get(pk=pipeline_stage_id)
                pipeline_id = stage.pipeline_id
            except PipelineStage.DoesNotExist:
                pass
        
        # Create lead
        lead = Lead.objects.create(
            external_id=str(uuid.uuid4()),
            team_id=user.current_crm_team.id if user.current_crm_team else None,
            person=person,
            organisation=organisation,
            client=client,
            title=data.get('title'),
            description=data.get('description'),
            amount=LeadService._convert_to_cents(data.get('amount')),
            currency=data.get('currency', 'USD'),
            lead_status_id=data.get('lead_status_id') or LeadService._get_default_status_id(),
            lead_source_id=data.get('lead_source_id'),
            user_owner_id=data.get('user_owner_id'),
            user_assigned_id=data.get('user_assigned_id'),
            pipeline_id=pipeline_id,
            pipeline_stage_id=pipeline_stage_id,
            expected_close=data.get('expected_close'),
            user_created=user,
        )
        
        # Sync labels
        LeadService._sync_labels(lead, data.get('labels', []))
        
        # Generate lead_id with prefix
        lead.lead_id = f"L-{lead.id:06d}"
        lead.save(update_fields=['lead_id'])
        
        return lead
    
    @staticmethod
    @transaction.atomic
    def update(lead, user, data, person=None, organisation=None, client=None):
        """
        Update a lead.
        Replicates Laravel's LeadService::update().
        """
        # Get pipeline from pipeline_stage
        pipeline_stage_id = data.get('pipeline_stage_id', lead.pipeline_stage_id)
        if pipeline_stage_id and pipeline_stage_id != lead.pipeline_stage_id:
            try:
                stage = PipelineStage.objects.get(pk=pipeline_stage_id)
                lead.pipeline_id = stage.pipeline_id
            except PipelineStage.DoesNotExist:
                pass
        
        lead.person = person if person is not None else lead.person
        lead.organisation = organisation if organisation is not None else lead.organisation
        lead.client = client if client is not None else lead.client
        lead.title = data.get('title', lead.title)
        lead.description = data.get('description', lead.description)
        
        if 'amount' in data:
            lead.amount = LeadService._convert_to_cents(data.get('amount'))
        
        lead.currency = data.get('currency', lead.currency)
        lead.lead_status_id = data.get('lead_status_id', lead.lead_status_id)
        lead.lead_source_id = data.get('lead_source_id', lead.lead_source_id)
        lead.user_owner_id = data.get('user_owner_id', lead.user_owner_id)
        lead.user_assigned_id = data.get('user_assigned_id', lead.user_assigned_id)
        lead.pipeline_stage_id = pipeline_stage_id
        lead.expected_close = data.get('expected_close', lead.expected_close)
        lead.user_updated = user
        lead.save()
        
        # Sync labels
        if 'labels' in data:
            LeadService._sync_labels(lead, data.get('labels', []))
        
        return lead
    
    @staticmethod
    @transaction.atomic
    def delete(lead, user):
        """Soft delete a lead."""
        lead.is_deleted = True
        lead.deleted_at = timezone.now()
        lead.user_deleted = user
        lead.save()
        return True
    
    @staticmethod
    def restore(lead, user):
        """Restore a soft-deleted lead."""
        lead.is_deleted = False
        lead.deleted_at = None
        lead.user_restored = user
        lead.save()
        return lead
    
    @staticmethod
    @transaction.atomic
    def convert_to_deal(lead, user, data, person=None, organisation=None, client=None):
        """
        Convert a lead to a deal.
        Replicates Laravel's LeadController::storeAsDeal().
        """
        # Create deal from lead
        deal = DealService.create(
            user=user,
            data={
                'title': data.get('title', lead.title),
                'description': data.get('description', lead.description),
                'amount': data.get('amount', lead.get_amount()),
                'currency': data.get('currency', lead.currency),
                'pipeline_stage_id': data.get('pipeline_stage_id'),
                'user_owner_id': data.get('user_owner_id', lead.user_owner_id),
                'user_assigned_id': data.get('user_assigned_id', lead.user_assigned_id),
                'expected_close': data.get('expected_close', lead.expected_close),
                'labels': data.get('labels', []),
                'lead_id': lead.id,
            },
            person=person or lead.person,
            organisation=organisation or lead.organisation,
            client=client or lead.client,
        )
        
        # Mark lead as converted
        lead.converted_at = timezone.now()
        lead.user_updated = user
        lead.save()
        
        return deal
    
    @staticmethod
    def _convert_to_cents(value):
        """Convert currency value to cents."""
        if value is None:
            return None
        return int(float(value) * 100)
    
    @staticmethod
    def _get_default_status_id():
        """Get the default lead status ID."""
        status = LeadStatus.objects.filter(is_deleted=False).order_by('order').first()
        return status.id if status else None
    
    @staticmethod
    def _sync_labels(lead, label_ids):
        """Sync lead labels."""
        content_type = ContentType.objects.get_for_model(Lead)
        
        Labelable.objects.filter(
            labelable_type=content_type,
            labelable_id=lead.id
        ).delete()
        
        for label_id in label_ids or []:
            Labelable.objects.create(
                label_id=label_id,
                labelable_type=content_type,
                labelable_id=lead.id
            )


class DealService:
    """
    Service for deal business logic.
    Replicates Laravel's DealService.
    """
    
    @staticmethod
    @transaction.atomic
    def create(user, data, person=None, organisation=None, client=None):
        """
        Create a new deal.
        Replicates Laravel's DealService::create().
        """
        # Get pipeline from pipeline_stage
        pipeline_id = None
        pipeline_stage_id = data.get('pipeline_stage_id')
        if pipeline_stage_id:
            try:
                stage = PipelineStage.objects.get(pk=pipeline_stage_id)
                pipeline_id = stage.pipeline_id
            except PipelineStage.DoesNotExist:
                pass
        
        # Create deal
        deal = Deal.objects.create(
            external_id=str(uuid.uuid4()),
            team_id=user.current_crm_team.id if user.current_crm_team else None,
            lead_id=data.get('lead_id'),
            person=person,
            organisation=organisation,
            client=client,
            title=data.get('title'),
            description=data.get('description'),
            amount=DealService._convert_to_cents(data.get('amount')),
            currency=data.get('currency', 'USD'),
            expected_close=data.get('expected_close'),
            user_owner_id=data.get('user_owner_id'),
            user_assigned_id=data.get('user_assigned_id'),
            pipeline_id=pipeline_id,
            pipeline_stage_id=pipeline_stage_id,
            user_created=user,
        )
        
        # Sync labels
        DealService._sync_labels(deal, data.get('labels', []))
        
        # Generate deal_id with prefix
        deal.deal_id = f"D-{deal.id:06d}"
        deal.save(update_fields=['deal_id'])
        
        # Handle deal products
        products = data.get('products', [])
        for idx, product_data in enumerate(products):
            DealService._create_deal_product(deal, product_data, idx, user)
        
        return deal
    
    @staticmethod
    @transaction.atomic
    def update(deal, user, data, person=None, organisation=None, client=None):
        """
        Update a deal.
        Replicates Laravel's DealService::update().
        """
        # Get pipeline from pipeline_stage
        pipeline_stage_id = data.get('pipeline_stage_id', deal.pipeline_stage_id)
        if pipeline_stage_id and pipeline_stage_id != deal.pipeline_stage_id:
            try:
                stage = PipelineStage.objects.get(pk=pipeline_stage_id)
                deal.pipeline_id = stage.pipeline_id
            except PipelineStage.DoesNotExist:
                pass
        
        deal.person = person if person is not None else deal.person
        deal.organisation = organisation if organisation is not None else deal.organisation
        deal.client = client if client is not None else deal.client
        deal.title = data.get('title', deal.title)
        deal.description = data.get('description', deal.description)
        
        if 'amount' in data:
            deal.amount = DealService._convert_to_cents(data.get('amount'))
        
        deal.currency = data.get('currency', deal.currency)
        deal.expected_close = data.get('expected_close', deal.expected_close)
        deal.user_owner_id = data.get('user_owner_id', deal.user_owner_id)
        deal.user_assigned_id = data.get('user_assigned_id', deal.user_assigned_id)
        deal.pipeline_stage_id = pipeline_stage_id
        deal.user_updated = user
        deal.save()
        
        # Sync labels
        if 'labels' in data:
            DealService._sync_labels(deal, data.get('labels', []))
        
        # Handle deal products updates
        if 'products' in data:
            existing_ids = []
            for idx, product_data in enumerate(data.get('products', [])):
                if product_data.get('id'):
                    DealService._update_deal_product(product_data, user)
                    existing_ids.append(product_data.get('id'))
                else:
                    dp = DealService._create_deal_product(deal, product_data, idx, user)
                    existing_ids.append(dp.id)
        
        return deal
    
    @staticmethod
    @transaction.atomic
    def delete(deal, user):
        """Soft delete a deal."""
        deal.is_deleted = True
        deal.deleted_at = timezone.now()
        deal.user_deleted = user
        deal.save()
        return True
    
    @staticmethod
    def restore(deal, user):
        """Restore a soft-deleted deal."""
        deal.is_deleted = False
        deal.deleted_at = None
        deal.user_restored = user
        deal.save()
        return deal
    
    @staticmethod
    @transaction.atomic
    def close_deal(deal, user, status, closed_at=None):
        """
        Close a deal as won or lost.
        """
        if status not in ['won', 'lost']:
            raise ValueError("Status must be 'won' or 'lost'")
        
        deal.closed_status = status
        deal.closed_at = closed_at or timezone.now()
        deal.user_updated = user
        deal.save()
        
        return deal
    
    @staticmethod
    @transaction.atomic
    def reopen_deal(deal, user):
        """Reopen a closed deal."""
        deal.closed_status = None
        deal.closed_at = None
        deal.user_updated = user
        deal.save()
        return deal
    
    @staticmethod
    @transaction.atomic
    def move_to_stage(deal, stage_id, user):
        """Move deal to a different pipeline stage."""
        try:
            stage = PipelineStage.objects.get(pk=stage_id)
            deal.pipeline_stage_id = stage_id
            deal.pipeline_id = stage.pipeline_id
            deal.user_updated = user
            deal.save()
            return deal
        except PipelineStage.DoesNotExist:
            raise ValueError("Pipeline stage not found")
    
    @staticmethod
    def _convert_to_cents(value):
        """Convert currency value to cents."""
        if value is None:
            return None
        return int(float(value) * 100)
    
    @staticmethod
    def _sync_labels(deal, label_ids):
        """Sync deal labels."""
        content_type = ContentType.objects.get_for_model(Deal)
        
        Labelable.objects.filter(
            labelable_type=content_type,
            labelable_id=deal.id
        ).delete()
        
        for label_id in label_ids or []:
            Labelable.objects.create(
                label_id=label_id,
                labelable_type=content_type,
                labelable_id=deal.id
            )
    
    @staticmethod
    def _create_deal_product(deal, product_data, order, user):
        """Create a deal product line item."""
        price = DealService._convert_to_cents(product_data.get('price'))
        quantity = product_data.get('quantity', 1)
        amount = price * quantity if price else None
        
        return DealProduct.objects.create(
            external_id=str(uuid.uuid4()),
            team_id=deal.team_id,
            deal=deal,
            product_id=product_data.get('product_id'),
            price=price,
            quantity=quantity,
            amount=amount,
            comments=product_data.get('comments'),
            order=order,
            user_created=user,
        )
    
    @staticmethod
    def _update_deal_product(product_data, user):
        """Update a deal product line item."""
        try:
            dp = DealProduct.objects.get(pk=product_data.get('id'))
            dp.product_id = product_data.get('product_id', dp.product_id)
            dp.price = DealService._convert_to_cents(product_data.get('price')) if 'price' in product_data else dp.price
            dp.quantity = product_data.get('quantity', dp.quantity)
            dp.amount = dp.price * dp.quantity if dp.price and dp.quantity else dp.amount
            dp.comments = product_data.get('comments', dp.comments)
            dp.user_updated = user
            dp.save()
            return dp
        except DealProduct.DoesNotExist:
            return None
