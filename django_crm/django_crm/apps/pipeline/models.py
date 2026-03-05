from django.db import models


class Pipeline(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'pipelines'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class PipelineStageProbability(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    percent = models.PositiveSmallIntegerField()
    limit = models.SmallIntegerField(null=True, blank=True)
    archive = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'pipeline_stage_probabilities'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.percent}%)"


class PipelineStage(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.CASCADE,
        related_name='stages'
    )
    pipeline_stage_probability = models.ForeignKey(
        PipelineStageProbability,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stages'
    )
    order = models.SmallIntegerField(default=0)
    color = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'pipeline_stages'
        ordering = ['order']

    def __str__(self):
        return f"{self.pipeline.name} - {self.name}"


class LeadStatus(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    order = models.SmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'lead_statuses'
        ordering = ['order']

    def __str__(self):
        return self.name


class LeadSource(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'lead_sources'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Lead(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads'
    )
    pipeline_stage = models.ForeignKey(
        PipelineStage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads'
    )
    pipeline_stage_order = models.IntegerField(null=True, blank=True)
    person = models.ForeignKey(
        'crm.Person',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads',
        db_index=True
    )
    organisation = models.ForeignKey(
        'crm.Organisation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads',
        db_index=True
    )
    client = models.ForeignKey(
        'crm.Organisation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='client_leads'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    lead_id = models.CharField(max_length=255, null=True, blank=True)
    prefix = models.CharField(max_length=255, null=True, blank=True)
    number = models.IntegerField(null=True, blank=True)
    amount = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    lead_status = models.ForeignKey(
        LeadStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads',
        db_index=True
    )
    lead_source = models.ForeignKey(
        LeadSource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads',
        db_index=True
    )
    qualified = models.BooleanField(default=False)
    expected_close = models.DateTimeField(null=True, blank=True)
    converted_at = models.DateTimeField(null=True, blank=True)
    user_created = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads_created'
    )
    user_updated = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads_updated'
    )
    user_deleted = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads_deleted'
    )
    user_restored = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads_restored'
    )
    user_owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads_owned'
    )
    user_assigned = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads_assigned'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'leads'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Deal(models.Model):
    CLOSED_STATUS_CHOICES = [
        ('won', 'Won'),
        ('lost', 'Lost'),
    ]

    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deals'
    )
    pipeline_stage = models.ForeignKey(
        PipelineStage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deals'
    )
    pipeline_stage_order = models.IntegerField(null=True, blank=True)
    lead = models.ForeignKey(
        Lead,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deals',
        db_index=True
    )
    person = models.ForeignKey(
        'crm.Person',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deals',
        db_index=True
    )
    organisation = models.ForeignKey(
        'crm.Organisation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deals',
        db_index=True
    )
    client = models.ForeignKey(
        'crm.Organisation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='client_deals'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    deal_id = models.CharField(max_length=255, null=True, blank=True)
    prefix = models.CharField(max_length=255, null=True, blank=True)
    number = models.IntegerField(null=True, blank=True)
    amount = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    qualified = models.BooleanField(default=False)
    expected_close = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_status = models.CharField(
        max_length=10,
        choices=CLOSED_STATUS_CHOICES,
        null=True,
        blank=True
    )
    user_created = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deals_created'
    )
    user_updated = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deals_updated'
    )
    user_deleted = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deals_deleted'
    )
    user_restored = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deals_restored'
    )
    user_owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deals_owned'
    )
    user_assigned = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deals_assigned'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'deals'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class DealProduct(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    deal = models.ForeignKey(
        Deal,
        on_delete=models.CASCADE,
        related_name='deal_products',
        db_index=True
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deal_products',
        db_index=True
    )
    product_variation = models.ForeignKey(
        'products.ProductVariation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deal_products',
        db_index=True
    )
    price = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tax_amount = models.IntegerField(null=True, blank=True)
    amount = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    order_field = models.IntegerField(null=True, blank=True, db_column='order')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'deal_products'
        ordering = ['order_field', '-created_at']

    def __str__(self):
        return f"{self.deal.title} - {self.product.name if self.product else 'N/A'}"
