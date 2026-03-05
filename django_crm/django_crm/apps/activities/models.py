from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Activity(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    log_name = models.CharField(max_length=255, default='default')
    description = models.CharField(max_length=255, null=True, blank=True)
    causeable_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='caused_activities'
    )
    causeable_id = models.BigIntegerField(null=True, blank=True)
    causeable = GenericForeignKey('causeable_type', 'causeable_id')
    timelineable_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='timeline_activities'
    )
    timelineable_id = models.BigIntegerField(null=True, blank=True)
    timelineable = GenericForeignKey('timelineable_type', 'timelineable_id')
    recordable_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_activities'
    )
    recordable_id = models.BigIntegerField(null=True, blank=True)
    recordable = GenericForeignKey('recordable_type', 'recordable_id')
    event = models.CharField(max_length=255, null=True, blank=True)
    properties = models.JSONField(null=True, blank=True)
    modified = models.JSONField(null=True, blank=True)
    ip_address = models.CharField(max_length=64, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'activities'
        ordering = ['-created_at']

    def __str__(self):
        return self.description or f"Activity #{self.pk}"


class Task(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    reminder_email = models.BooleanField(default=False)
    reminder_sms = models.BooleanField(default=False)
    taskable_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )
    taskable_id = models.BigIntegerField(null=True, blank=True)
    taskable = GenericForeignKey('taskable_type', 'taskable_id')
    user_created = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_created'
    )
    user_updated = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_updated'
    )
    user_deleted = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_deleted'
    )
    user_restored = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_restored'
    )
    user_owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_owned'
    )
    user_assigned = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_assigned'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'tasks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['taskable_type', 'taskable_id']),
        ]

    def __str__(self):
        return self.name


class Call(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    start_at = models.DateTimeField(null=True, blank=True)
    finish_at = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    reminder_email = models.BooleanField(default=False)
    reminder_sms = models.BooleanField(default=False)
    callable_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calls'
    )
    callable_id = models.BigIntegerField(null=True, blank=True)
    callable_obj = GenericForeignKey('callable_type', 'callable_id')
    user_created = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calls_created'
    )
    user_updated = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calls_updated'
    )
    user_deleted = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calls_deleted'
    )
    user_restored = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calls_restored'
    )
    user_owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calls_owned'
    )
    user_assigned = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calls_assigned'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'calls'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['callable_type', 'callable_id']),
        ]

    def __str__(self):
        return self.name


class Meeting(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    start_at = models.DateTimeField(null=True, blank=True)
    finish_at = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    reminder_email = models.BooleanField(default=False)
    reminder_sms = models.BooleanField(default=False)
    meetingable_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meetings'
    )
    meetingable_id = models.BigIntegerField(null=True, blank=True)
    meetingable = GenericForeignKey('meetingable_type', 'meetingable_id')
    user_created = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meetings_created'
    )
    user_updated = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meetings_updated'
    )
    user_deleted = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meetings_deleted'
    )
    user_restored = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meetings_restored'
    )
    user_owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meetings_owned'
    )
    user_assigned = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meetings_assigned'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'meetings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['meetingable_type', 'meetingable_id']),
        ]

    def __str__(self):
        return self.name


class Lunch(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    start_at = models.DateTimeField(null=True, blank=True)
    finish_at = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    reminder_email = models.BooleanField(default=False)
    reminder_sms = models.BooleanField(default=False)
    lunchable_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lunches'
    )
    lunchable_id = models.BigIntegerField(null=True, blank=True)
    lunchable = GenericForeignKey('lunchable_type', 'lunchable_id')
    user_created = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lunches_created'
    )
    user_updated = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lunches_updated'
    )
    user_deleted = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lunches_deleted'
    )
    user_restored = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lunches_restored'
    )
    user_owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lunches_owned'
    )
    user_assigned = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lunches_assigned'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'lunches'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['lunchable_type', 'lunchable_id']),
        ]

    def __str__(self):
        return self.name
