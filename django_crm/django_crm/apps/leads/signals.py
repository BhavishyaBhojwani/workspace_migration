from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from apps.crm.models import Activity


@receiver(post_save)
def log_lead_activity(sender, instance, created, **kwargs):
    """Log lead activities."""
    if sender.__name__ == 'Lead':
        from .models import Lead
        
        if created:
            Activity.objects.create(
                log_name='default',
                description='Lead created',
                causeable_type=ContentType.objects.get_for_model(instance.user_created.__class__),
                causeable_id=instance.user_created_id,
                recordable_type=ContentType.objects.get_for_model(Lead),
                recordable_id=instance.id,
                event='lead_created',
                properties={
                    'lead_id': instance.id,
                    'lead_title': instance.title
                }
            )
        else:
            Activity.objects.create(
                log_name='default',
                description='Lead updated',
                causeable_type=ContentType.objects.get_for_model(instance.user_updated.__class__),
                causeable_id=instance.user_updated_id,
                recordable_type=ContentType.objects.get_for_model(Lead),
                recordable_id=instance.id,
                event='lead_updated',
                properties={
                    'lead_id': instance.id,
                    'lead_title': instance.title
                }
            )


@receiver(post_delete)
def log_lead_deletion(sender, instance, **kwargs):
    """Log lead deletion."""
    if sender.__name__ == 'Lead':
        from .models import Lead
        
        Activity.objects.create(
            log_name='default',
            description='Lead deleted',
            causeable_type=ContentType.objects.get_for_model(instance.user_deleted.__class__),
            causeable_id=instance.user_deleted_id,
            recordable_type=ContentType.objects.get_for_model(Lead),
            recordable_id=instance.id,
            event='lead_deleted',
            properties={
                'lead_id': instance.id,
                'lead_title': instance.title
            }
        )
