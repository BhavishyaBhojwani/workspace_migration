from django.db import models


class PurchaseOrder(models.Model):
    DELIVERY_TYPE_CHOICES = [
        ('deliver', 'Deliver'),
        ('pickup', 'Pickup'),
    ]

    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    pipeline = models.ForeignKey(
        'pipeline.Pipeline',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_orders'
    )
    pipeline_stage = models.ForeignKey(
        'pipeline.PipelineStage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_orders'
    )
    pipeline_stage_order = models.IntegerField(null=True, blank=True)
    order = models.ForeignKey(
        'sales.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_orders',
        db_index=True
    )
    person = models.ForeignKey(
        'crm.Person',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_orders',
        db_index=True
    )
    organisation = models.ForeignKey(
        'crm.Organisation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_orders',
        db_index=True
    )
    reference = models.CharField(max_length=255, null=True, blank=True)
    purchase_order_id = models.CharField(max_length=255)
    prefix = models.CharField(max_length=255, null=True, blank=True)
    number = models.BigIntegerField()
    issue_date = models.DateField(null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    subtotal = models.IntegerField(null=True, blank=True)
    discount = models.IntegerField(null=True, blank=True)
    tax = models.IntegerField(null=True, blank=True)
    adjustments = models.IntegerField(null=True, blank=True)
    total = models.IntegerField(null=True, blank=True)
    delivery_type = models.CharField(
        max_length=10,
        choices=DELIVERY_TYPE_CHOICES,
        default='deliver'
    )
    delivery_instructions = models.TextField(null=True, blank=True)
    terms = models.TextField(null=True, blank=True)
    sent = models.BooleanField(default=False)
    user_created = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_orders_created'
    )
    user_updated = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_orders_updated'
    )
    user_deleted = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_orders_deleted'
    )
    user_restored = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_orders_restored'
    )
    user_owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_orders_owned'
    )
    user_assigned = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_orders_assigned'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'purchase_orders'
        ordering = ['-created_at']

    def __str__(self):
        return self.purchase_order_id


class PurchaseOrderLine(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='lines',
        db_index=True
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_order_lines',
        db_index=True
    )
    product_variation = models.ForeignKey(
        'products.ProductVariation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_order_lines',
        db_index=True
    )
    description = models.TextField(null=True, blank=True)
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
        db_table = 'purchase_order_lines'
        ordering = ['order_field', '-created_at']

    def __str__(self):
        return f"{self.purchase_order.purchase_order_id} - Line {self.pk}"
