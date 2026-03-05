from django.db import models


class Quote(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    pipeline = models.ForeignKey(
        'pipeline.Pipeline',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotes'
    )
    pipeline_stage = models.ForeignKey(
        'pipeline.PipelineStage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotes'
    )
    pipeline_stage_order = models.IntegerField(null=True, blank=True)
    lead = models.ForeignKey(
        'pipeline.Lead',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotes',
        db_index=True
    )
    deal = models.ForeignKey(
        'pipeline.Deal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotes',
        db_index=True
    )
    person = models.ForeignKey(
        'crm.Person',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotes',
        db_index=True
    )
    organisation = models.ForeignKey(
        'crm.Organisation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotes',
        db_index=True
    )
    client = models.ForeignKey(
        'crm.Organisation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='client_quotes'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    reference = models.CharField(max_length=255, null=True, blank=True)
    quote_id = models.CharField(max_length=255, null=True, blank=True)
    prefix = models.CharField(max_length=255, null=True, blank=True)
    number = models.IntegerField(null=True, blank=True)
    issue_at = models.DateTimeField(null=True, blank=True)
    expire_at = models.DateTimeField(null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    subtotal = models.IntegerField(null=True, blank=True)
    discount = models.IntegerField(null=True, blank=True)
    tax = models.IntegerField(null=True, blank=True)
    adjustments = models.IntegerField(null=True, blank=True)
    total = models.IntegerField(null=True, blank=True)
    terms = models.TextField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    user_created = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotes_created'
    )
    user_updated = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotes_updated'
    )
    user_deleted = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotes_deleted'
    )
    user_restored = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotes_restored'
    )
    user_owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotes_owned'
    )
    user_assigned = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotes_assigned'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'quotes'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class QuoteProduct(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    quote = models.ForeignKey(
        Quote,
        on_delete=models.CASCADE,
        related_name='quote_products',
        db_index=True
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quote_products',
        db_index=True
    )
    product_variation = models.ForeignKey(
        'products.ProductVariation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quote_products',
        db_index=True
    )
    price = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tax_amount = models.IntegerField(null=True, blank=True)
    amount = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    comments = models.CharField(max_length=255, null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'quote_products'
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.quote.title} - {self.product.name if self.product else 'N/A'}"


class Order(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    pipeline = models.ForeignKey(
        'pipeline.Pipeline',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    pipeline_stage = models.ForeignKey(
        'pipeline.PipelineStage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    pipeline_stage_order = models.IntegerField(null=True, blank=True)
    lead = models.ForeignKey(
        'pipeline.Lead',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        db_index=True
    )
    deal = models.ForeignKey(
        'pipeline.Deal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        db_index=True
    )
    quote = models.ForeignKey(
        Quote,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        db_index=True
    )
    client = models.ForeignKey(
        'crm.Organisation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='client_orders'
    )
    person = models.ForeignKey(
        'crm.Person',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        db_index=True
    )
    organisation = models.ForeignKey(
        'crm.Organisation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        db_index=True
    )
    description = models.TextField(null=True, blank=True)
    reference = models.CharField(max_length=255, null=True, blank=True)
    order_id = models.CharField(max_length=255, null=True, blank=True)
    prefix = models.CharField(max_length=255, null=True, blank=True)
    number = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    subtotal = models.IntegerField(null=True, blank=True)
    discount = models.IntegerField(null=True, blank=True)
    tax = models.IntegerField(null=True, blank=True)
    adjustments = models.IntegerField(null=True, blank=True)
    total = models.IntegerField(null=True, blank=True)
    terms = models.TextField(null=True, blank=True)
    user_created = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders_created'
    )
    user_updated = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders_updated'
    )
    user_deleted = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders_deleted'
    )
    user_restored = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders_restored'
    )
    user_owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders_owned'
    )
    user_assigned = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders_assigned'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']

    def __str__(self):
        return self.order_id or f"Order #{self.pk}"


class OrderProduct(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_products',
        db_index=True
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_products',
        db_index=True
    )
    product_variation = models.ForeignKey(
        'products.ProductVariation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_products',
        db_index=True
    )
    price = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tax_amount = models.IntegerField(null=True, blank=True)
    amount = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    comments = models.CharField(max_length=255, null=True, blank=True)
    quote_product = models.ForeignKey(
        QuoteProduct,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_products'
    )
    order_field = models.IntegerField(null=True, blank=True, db_column='order')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'order_products'
        ordering = ['order_field', '-created_at']

    def __str__(self):
        return f"{self.order} - {self.product.name if self.product else 'N/A'}"


class Invoice(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    pipeline = models.ForeignKey(
        'pipeline.Pipeline',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices'
    )
    pipeline_stage = models.ForeignKey(
        'pipeline.PipelineStage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices'
    )
    pipeline_stage_order = models.IntegerField(null=True, blank=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        db_index=True
    )
    person = models.ForeignKey(
        'crm.Person',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        db_index=True
    )
    organisation = models.ForeignKey(
        'crm.Organisation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        db_index=True
    )
    reference = models.CharField(max_length=255, null=True, blank=True)
    invoice_id = models.CharField(max_length=255)
    prefix = models.CharField(max_length=255, null=True, blank=True)
    number = models.BigIntegerField()
    issue_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    subtotal = models.IntegerField(null=True, blank=True)
    discount = models.IntegerField(null=True, blank=True)
    tax = models.IntegerField(null=True, blank=True)
    adjustments = models.IntegerField(null=True, blank=True)
    total = models.IntegerField(null=True, blank=True)
    terms = models.TextField(null=True, blank=True)
    sent = models.BooleanField(default=False)
    amount_due = models.IntegerField(null=True, blank=True)
    amount_paid = models.IntegerField(null=True, blank=True)
    fully_paid_at = models.DateTimeField(null=True, blank=True)
    user_created = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices_created'
    )
    user_updated = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices_updated'
    )
    user_deleted = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices_deleted'
    )
    user_restored = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices_restored'
    )
    user_owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices_owned'
    )
    user_assigned = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices_assigned'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']

    def __str__(self):
        return self.invoice_id


class InvoiceLine(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='invoice_lines',
        db_index=True
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoice_lines',
        db_index=True
    )
    product_variation = models.ForeignKey(
        'products.ProductVariation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoice_lines',
        db_index=True
    )
    order_product = models.ForeignKey(
        OrderProduct,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoice_lines',
        db_index=True
    )
    description = models.TextField(null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tax_amount = models.IntegerField(null=True, blank=True)
    amount = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    comments = models.CharField(max_length=255, null=True, blank=True)
    order_field = models.IntegerField(null=True, blank=True, db_column='order')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'invoice_lines'
        ordering = ['order_field', '-created_at']

    def __str__(self):
        return f"{self.invoice.invoice_id} - Line {self.pk}"


class Delivery(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    pipeline = models.ForeignKey(
        'pipeline.Pipeline',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries'
    )
    pipeline_stage = models.ForeignKey(
        'pipeline.PipelineStage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries'
    )
    pipeline_stage_order = models.IntegerField(null=True, blank=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries',
        db_index=True
    )
    delivery_id = models.CharField(max_length=255, null=True, blank=True)
    prefix = models.CharField(max_length=255, null=True, blank=True)
    number = models.IntegerField(null=True, blank=True)
    delivery_initiated = models.DateTimeField(null=True, blank=True)
    delivery_shipped = models.DateTimeField(null=True, blank=True)
    delivery_expected = models.DateTimeField(null=True, blank=True)
    delivered_on = models.DateTimeField(null=True, blank=True)
    user_created = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries_created'
    )
    user_updated = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries_updated'
    )
    user_deleted = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries_deleted'
    )
    user_restored = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries_restored'
    )
    user_owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries_owned'
    )
    user_assigned = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries_assigned'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'deliveries'
        ordering = ['-created_at']

    def __str__(self):
        return self.delivery_id or f"Delivery #{self.pk}"


class DeliveryProduct(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    delivery = models.ForeignKey(
        Delivery,
        on_delete=models.CASCADE,
        related_name='delivery_products',
        db_index=True
    )
    order_product = models.ForeignKey(
        OrderProduct,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='delivery_products',
        db_index=True
    )
    quantity = models.IntegerField(null=True, blank=True)
    order_field = models.IntegerField(null=True, blank=True, db_column='order')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'delivery_products'
        ordering = ['order_field', '-created_at']

    def __str__(self):
        return f"{self.delivery} - Product {self.pk}"
