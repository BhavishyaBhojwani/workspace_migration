from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Audit(models.Model):
    """Audit trail for tracking changes to models."""
    user_type = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.PositiveBigIntegerField(blank=True, null=True)
    event = models.CharField(max_length=255)
    auditable_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='audits'
    )
    auditable_id = models.PositiveBigIntegerField()
    auditable = GenericForeignKey('auditable_type', 'auditable_id')
    old_values = models.TextField(blank=True, null=True)
    new_values = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=1023, blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'audits'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id', 'user_type']),
        ]

    def __str__(self):
        return f"{self.event} on {self.auditable_type} #{self.auditable_id}"


class UsageRequest(models.Model):
    """Tracks usage requests for analytics."""
    team = models.ForeignKey(
        'accounts.Team',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='usage_requests'
    )
    host = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    url = models.CharField(max_length=2048)
    method = models.CharField(max_length=255)
    route = models.CharField(max_length=255)
    visitor = models.CharField(max_length=255, blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    response_time = models.IntegerField(blank=True, null=True)
    day = models.CharField(max_length=255, blank=True, null=True)
    hour = models.SmallIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'laravel_crm_usage_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.method} {self.path}"
