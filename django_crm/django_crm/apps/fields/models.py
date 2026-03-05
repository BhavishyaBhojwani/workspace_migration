from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class FieldGroup(models.Model):
    """Groups for organizing custom fields."""
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    handle = models.CharField(max_length=255, null=True, blank=True)
    system = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'field_groups'
        ordering = ['name']

    def __str__(self):
        return self.name


class Field(models.Model):
    """Custom field definitions for CRM entities."""
    TYPE_CHOICES = [
        ('text', 'Text'),
        ('textarea', 'Textarea'),
        ('select', 'Select'),
        ('select_multiple', 'Select Multiple'),
        ('checkbox', 'Checkbox'),
        ('checkbox_multiple', 'Checkbox Multiple'),
        ('radio', 'Radio'),
        ('date', 'Date'),
    ]

    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    field_group = models.ForeignKey(
        FieldGroup,
        on_delete=models.CASCADE,
        related_name='fields',
        db_index=True
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='text')
    name = models.CharField(max_length=255)
    handle = models.CharField(max_length=255, null=True, blank=True)
    required = models.BooleanField(default=False)
    default = models.CharField(max_length=255, null=True, blank=True)
    config = models.JSONField(null=True, blank=True)
    validation = models.JSONField(null=True, blank=True)
    system = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'fields'
        ordering = ['name']

    def __str__(self):
        return self.name


class FieldModel(models.Model):
    """Maps fields to specific model types."""
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        related_name='field_models',
        db_index=True
    )
    model = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'field_models'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.field.name} → {self.model}"


class FieldOption(models.Model):
    """Options for select/checkbox/radio field types."""
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        related_name='options',
        db_index=True
    )
    value = models.CharField(max_length=255, null=True, blank=True)
    label = models.CharField(max_length=255, null=True, blank=True)
    order = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'field_options'
        ordering = ['order', 'label']

    def __str__(self):
        return self.label or self.value or str(self.pk)


class FieldValue(models.Model):
    """Stored values for custom fields on entities."""
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='values')
    field_valueable_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    field_valueable_id = models.BigIntegerField()
    field_valueable = GenericForeignKey('field_valueable_type', 'field_valueable_id')
    value = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'field_values'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['field_valueable_type', 'field_valueable_id']),
        ]

    def __str__(self):
        return f"{self.field.name}: {self.value[:50]}"
