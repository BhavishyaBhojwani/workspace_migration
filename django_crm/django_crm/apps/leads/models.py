from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class LeadStatus(models.Model):
    """Lead status reference table."""
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    order = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'lead_statuses_new'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class LeadSource(models.Model):
    """Lead source reference table."""
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'lead_sources_new'
        ordering = ['name']

    def __str__(self):
        return self.name


class Lead(models.Model):
    """
    Lead model replicating Laravel CRM Lead structure.
    Maintains exact field names and relationships for frontend compatibility.
    """
    # Basic fields
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    
    # Relationships
    person = models.ForeignKey(
        "crm.Person",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="person_id",
        related_name="lead_contacts"
    )
    organisation = models.ForeignKey(
        "crm.Organisation",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="organisation_id",
        related_name="lead_organisations"
    )
    
    # Lead details
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    amount = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Status and source
    lead_status = models.ForeignKey(
        LeadStatus,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="lead_status_id"
    )
    lead_source = models.ForeignKey(
        LeadSource,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="lead_source_id"
    )
    
    # Lead lifecycle
    qualified = models.BooleanField(default=False)
    expected_close = models.DateTimeField(null=True, blank=True)
    converted_at = models.DateTimeField(null=True, blank=True)
    
    # User tracking (Laravel style with user_created_id pattern)
    user_created = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="user_created_id",
        related_name="created_leads"
    )
    user_updated = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="user_updated_id",
        related_name="updated_leads"
    )
    user_deleted = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="user_deleted_id",
        related_name="deleted_leads"
    )
    user_restored = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="user_restored_id",
        related_name="restored_leads"
    )
    user_owner = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="user_owner_id",
        related_name="owned_leads"
    )
    user_assigned = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="user_assigned_id",
        related_name="assigned_leads"
    )
    
    # Timestamps and soft delete
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Generic relations for labels, notes, etc.
    labels = GenericRelation('crm.Label')
    notes = GenericRelation('crm.Note')
    
    class Meta:
        db_table = 'leads_new'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['team_id']),
            models.Index(fields=['person']),
            models.Index(fields=['organisation']),
            models.Index(fields=['lead_status']),
            models.Index(fields=['lead_source']),
            models.Index(fields=['user_owner']),
            models.Index(fields=['user_assigned']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.title
    
    def soft_delete(self, user=None):
        """Soft delete the lead."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if user:
            self.user_deleted = user  # Pass User instance, not ID
        self.save()
    
    def restore(self, user=None):
        """Restore a soft deleted lead."""
        self.is_deleted = False
        self.deleted_at = None
        if user:
            self.user_restored = user
        self.save()
    
    def convert_to_deal(self):
        """Convert lead to deal."""
        from apps.pipeline.models import Deal
        from apps.crm.models import Organisation, Person
        
        # Create deal from lead
        deal = Deal.objects.create(
            external_id=self.external_id,
            team_id=self.team_id,
            person_id=self.person_id,
            organisation_id=self.organisation_id,
            title=self.title,
            description=self.description,
            amount=self.amount,
            currency=self.currency,
            user_created_id=self.user_created_id,
            user_owner_id=self.user_owner_id,
            user_assigned_id=self.user_assigned_id,
        )
        
        # Mark lead as converted
        self.converted_at = models.timezone.now()
        self.save()
        
        return deal
