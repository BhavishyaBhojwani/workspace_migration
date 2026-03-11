from django.contrib import admin
from .models import Lead, LeadStatus, LeadSource


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'person', 'organisation', 'lead_status_id', 
        'lead_source_id', 'amount', 'currency', 'qualified',
        'user_owner_id', 'created_at'
    ]
    list_filter = [
        'lead_status_id', 'lead_source_id', 'qualified', 'currency',
        'created_at', 'converted_at'
    ]
    search_fields = ['title', 'description']
    readonly_fields = [
        'external_id', 'created_at', 'updated_at', 
        'converted_at', 'deleted_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'person_id', 'organisation_id')
        }),
        ('Financial', {
            'fields': ('amount', 'currency')
        }),
        ('Status', {
            'fields': ('lead_status_id', 'lead_source_id', 'qualified')
        }),
        ('Timeline', {
            'fields': ('expected_close', 'converted_at')
        }),
        ('Ownership', {
            'fields': ('user_owner_id', 'user_assigned_id')
        }),
        ('System', {
            'fields': ('external_id', 'team_id', 'created_at', 'updated_at', 'deleted_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_deleted=False)


@admin.register(LeadStatus)
class LeadStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'created_at']
    list_editable = ['order']
    search_fields = ['name', 'description']


@admin.register(LeadSource)
class LeadSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name', 'description']
