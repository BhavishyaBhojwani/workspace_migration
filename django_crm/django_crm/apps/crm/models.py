from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


class Timezone(models.Model):
    """Timezone reference table."""
    name = models.CharField(max_length=255)
    offset = models.CharField(max_length=255)
    diff_from_gtm = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'timezones'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.offset})"


class Industry(models.Model):
    """Industry classification for organisations."""
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'industries'
        ordering = ['name']

    def __str__(self):
        return self.name


class OrganisationType(models.Model):
    """Classification type for organisations."""
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'organisation_types'
        ordering = ['name']

    def __str__(self):
        return self.name


class Organisation(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=1000)
    description = models.TextField(null=True, blank=True)
    # FK relationships
    organisation_type = models.ForeignKey(
        OrganisationType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organisations',
        db_index=True
    )
    industry = models.ForeignKey(
        Industry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organisations',
        db_index=True
    )
    timezone = models.ForeignKey(
        Timezone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organisations',
        db_index=True
    )
    # Financial fields
    vat_number = models.CharField(max_length=255, null=True, blank=True)
    annual_revenue = models.IntegerField(null=True, blank=True)
    total_money_raised = models.IntegerField(null=True, blank=True)
    number_of_employees = models.SmallIntegerField(null=True, blank=True)
    year_founded = models.SmallIntegerField(null=True, blank=True)
    # Domain/Website
    domain = models.CharField(max_length=255, null=True, blank=True)
    website_url = models.CharField(max_length=255, null=True, blank=True)
    # Social media fields
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    facebook = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    instagram = models.CharField(max_length=255, null=True, blank=True)
    youtube = models.CharField(max_length=255, null=True, blank=True)
    pinterest = models.CharField(max_length=255, null=True, blank=True)
    tiktok = models.CharField(max_length=255, null=True, blank=True)
    google = models.CharField(max_length=255, null=True, blank=True)
    # User tracking
    user_created = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organisations_created'
    )
    user_updated = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organisations_updated'
    )
    user_deleted = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organisations_deleted'
    )
    user_restored = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organisations_restored'
    )
    user_owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organisations_owned'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    emails = GenericRelation('crm.Email', content_type_field='emailable_type', object_id_field='emailable_id')
    phones = GenericRelation('crm.Phone', content_type_field='phoneable_type', object_id_field='phoneable_id')
    addresses = GenericRelation('crm.Address', content_type_field='addressable_type', object_id_field='addressable_id')
    notes = GenericRelation('crm.Note', content_type_field='noteable_type', object_id_field='noteable_id')
    labelables = GenericRelation('crm.Labelable', content_type_field='labelable_type', object_id_field='labelable_id')

    class Meta:
        db_table = 'organisations'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Person(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    title = models.CharField(max_length=500, null=True, blank=True)
    first_name = models.CharField(max_length=500)
    middle_name = models.CharField(max_length=500, null=True, blank=True)
    last_name = models.CharField(max_length=500, null=True, blank=True)
    maiden_name = models.CharField(max_length=500, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='people'
    )
    user_created = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='people_created'
    )
    user_updated = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='people_updated'
    )
    user_deleted = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='people_deleted'
    )
    user_restored = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='people_restored'
    )
    user_owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='people_owned'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    emails = GenericRelation('crm.Email', content_type_field='emailable_type', object_id_field='emailable_id')
    phones = GenericRelation('crm.Phone', content_type_field='phoneable_type', object_id_field='phoneable_id')
    addresses = GenericRelation('crm.Address', content_type_field='addressable_type', object_id_field='addressable_id')
    notes = GenericRelation('crm.Note', content_type_field='noteable_type', object_id_field='noteable_id')
    labelables = GenericRelation('crm.Labelable', content_type_field='labelable_type', object_id_field='labelable_id')

    class Meta:
        db_table = 'people'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''}".strip()


class Email(models.Model):
    TYPE_CHOICES = [
        ('work', 'Work'),
        ('home', 'Home'),
        ('other', 'Other'),
    ]

    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    primary = models.BooleanField(default=False)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='work', null=True, blank=True)
    emailable_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    emailable_id = models.BigIntegerField()
    emailable = GenericForeignKey('emailable_type', 'emailable_id')
    user_created = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emails_created'
    )
    user_updated = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emails_updated'
    )
    user_deleted = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emails_deleted'
    )
    user_restored = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emails_restored'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'emails'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['emailable_type', 'emailable_id']),
        ]

    def __str__(self):
        return self.address or ''


class Phone(models.Model):
    TYPE_CHOICES = [
        ('work', 'Work'),
        ('home', 'Home'),
        ('mobile', 'Mobile'),
        ('fax', 'Fax'),
        ('other', 'Other'),
    ]

    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    number = models.CharField(max_length=500, null=True, blank=True)
    primary = models.BooleanField(default=False)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='work', null=True, blank=True)
    phoneable_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    phoneable_id = models.BigIntegerField()
    phoneable = GenericForeignKey('phoneable_type', 'phoneable_id')
    user_created = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='phones_created'
    )
    user_updated = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='phones_updated'
    )
    user_deleted = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='phones_deleted'
    )
    user_restored = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='phones_restored'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'phones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phoneable_type', 'phoneable_id']),
        ]

    def __str__(self):
        return self.number or ''


class AddressType(models.Model):
    """Classification types for addresses."""
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'address_types'
        ordering = ['name']

    def __str__(self):
        return self.name


class Address(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    address_type = models.ForeignKey(
        AddressType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='addresses',
        db_index=True
    )
    address = models.CharField(max_length=1000, null=True, blank=True)
    name = models.CharField(max_length=1000, null=True, blank=True)
    contact = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    line1 = models.CharField(max_length=1000, null=True, blank=True)
    line2 = models.CharField(max_length=1000, null=True, blank=True)
    line3 = models.CharField(max_length=1000, null=True, blank=True)
    code = models.CharField(max_length=500, null=True, blank=True)
    city = models.CharField(max_length=500, null=True, blank=True)
    state = models.CharField(max_length=500, null=True, blank=True)
    country = models.CharField(max_length=500, null=True, blank=True)
    primary = models.BooleanField(default=False)
    addressable_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    addressable_id = models.BigIntegerField()
    addressable = GenericForeignKey('addressable_type', 'addressable_id')
    user_created = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='addresses_created'
    )
    user_updated = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='addresses_updated'
    )
    user_deleted = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='addresses_deleted'
    )
    user_restored = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='addresses_restored'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'addresses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['addressable_type', 'addressable_id']),
        ]

    def __str__(self):
        return self.address or f"{self.line1}, {self.city}"


class Note(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    content = models.TextField()
    pinned = models.BooleanField(default=False)
    noteable_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    noteable_id = models.BigIntegerField()
    noteable = GenericForeignKey('noteable_type', 'noteable_id')
    user_created = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notes_created'
    )
    user_updated = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notes_updated'
    )
    user_deleted = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notes_deleted'
    )
    user_restored = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notes_restored'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['noteable_type', 'noteable_id']),
        ]

    def __str__(self):
        return self.content[:50]


class Label(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    hex = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'labels'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Labelable(models.Model):
    label = models.ForeignKey(Label, on_delete=models.CASCADE)
    labelable_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    labelable_id = models.BigIntegerField()
    labelable = GenericForeignKey('labelable_type', 'labelable_id')

    class Meta:
        db_table = 'labelables'
        indexes = [
            models.Index(fields=['labelable_type', 'labelable_id']),
        ]

    def __str__(self):
        return f"{self.label.name}"


class Setting(models.Model):
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='settings'
    )
    global_setting = models.BooleanField(default=False, db_column='global')
    name = models.CharField(max_length=255)
    label = models.CharField(max_length=255, null=True, blank=True)
    value = models.CharField(max_length=255)
    editable = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'settings'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ContactType(models.Model):
    """Classification types for contacts."""
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'contact_types'
        ordering = ['name']

    def __str__(self):
        return self.name


class Contact(models.Model):
    """Links contactable entities to entityable targets."""
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    # Polymorphic: who is the contact (Person/Organisation)
    contactable_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='contacts_as_contactable'
    )
    contactable_id = models.BigIntegerField()
    contactable = GenericForeignKey('contactable_type', 'contactable_id')
    # Polymorphic: what entity they're a contact for
    entityable_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='contacts_as_entityable'
    )
    entityable_id = models.BigIntegerField()
    entityable = GenericForeignKey('entityable_type', 'entityable_id')
    # Many-to-many with ContactType via pivot
    contact_types = models.ManyToManyField(
        ContactType,
        through='ContactContactType',
        related_name='contacts'
    )
    # User tracking
    user_created = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contacts_created'
    )
    user_updated = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contacts_updated'
    )
    user_deleted = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contacts_deleted'
    )
    user_restored = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contacts_restored'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'contacts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['contactable_type', 'contactable_id']),
            models.Index(fields=['entityable_type', 'entityable_id']),
        ]

    def __str__(self):
        return f"Contact #{self.pk}"


class ContactContactType(models.Model):
    """Pivot table linking contacts to contact types."""
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        db_index=True
    )
    contact_type = models.ForeignKey(
        ContactType,
        on_delete=models.CASCADE,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'contact_contact_type'

    def __str__(self):
        return f"{self.contact} - {self.contact_type.name}"


class Client(models.Model):
    """Client entities linked polymorphically to organisations/people."""
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    # Polymorphic: what is the client (Organisation/Person)
    clientable_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='clients'
    )
    clientable_id = models.BigIntegerField()
    clientable = GenericForeignKey('clientable_type', 'clientable_id')
    # User tracking
    user_created = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clients_created'
    )
    user_updated = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clients_updated'
    )
    user_deleted = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clients_deleted'
    )
    user_restored = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clients_restored'
    )
    user_owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clients_owned'
    )
    user_assigned = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clients_assigned'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'clients'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['clientable_type', 'clientable_id']),
        ]

    def __str__(self):
        return self.name or f"Client #{self.pk}"


class File(models.Model):
    """Polymorphic file attachments for any CRM entity."""
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    # Polymorphic: what entity this file belongs to
    fileable_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='files'
    )
    fileable_id = models.BigIntegerField()
    fileable = GenericForeignKey('fileable_type', 'fileable_id')
    # File details
    file = models.CharField(max_length=255)
    name = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    format = models.CharField(max_length=255, null=True, blank=True)
    filesize = models.CharField(max_length=255, null=True, blank=True)
    mime = models.CharField(max_length=255, null=True, blank=True)
    disk = models.CharField(max_length=255, default='local')
    # User tracking
    user_created = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='files_created'
    )
    user_updated = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='files_updated'
    )
    user_deleted = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='files_deleted'
    )
    user_restored = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='files_restored'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'files'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['fileable_type', 'fileable_id']),
        ]

    def __str__(self):
        return self.name or self.file


# ============================================================================
# LEADS, PIPELINES & DEALS
# Note: These models are defined in apps.pipeline.models
# Import them here for convenience
# ============================================================================
from apps.pipeline.models import (
    LeadStatus,
    LeadSource,
    PipelineStageProbability,
    Pipeline,
    PipelineStage,
    Lead,
    Deal,
    DealProduct,
)
