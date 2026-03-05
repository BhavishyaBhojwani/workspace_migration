from django.db import models


class XeroToken(models.Model):
    """Xero OAuth token storage."""
    team = models.ForeignKey(
        'accounts.Team',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='xero_tokens'
    )
    id_token = models.TextField(blank=True, null=True)
    access_token = models.TextField()
    expires_in = models.CharField(max_length=255, blank=True, null=True)
    token_type = models.CharField(max_length=255, blank=True, null=True)
    refresh_token = models.CharField(max_length=255, blank=True, null=True)
    scopes = models.CharField(max_length=255)
    auth_event_id = models.CharField(max_length=255, blank=True, null=True)
    tenant_id = models.CharField(max_length=255, blank=True, null=True)
    tenant_type = models.CharField(max_length=255, blank=True, null=True)
    tenant_name = models.CharField(max_length=255, blank=True, null=True)
    created_date_utc = models.CharField(max_length=255, blank=True, null=True)
    updated_date_utc = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'xero_tokens'
        ordering = ['-created_at']

    def __str__(self):
        return f"XeroToken {self.tenant_name or self.id}"


class XeroItem(models.Model):
    """Xero product/item sync mapping."""
    external_id = models.CharField(max_length=255)
    team = models.ForeignKey(
        'accounts.Team',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='xero_items',
        db_index=True
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='xero_items'
    )
    item_id = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    inventory_tracked = models.BooleanField(default=False)
    is_purchased = models.BooleanField(default=False)
    purchase_price = models.IntegerField(blank=True, null=True)
    purchase_description = models.CharField(max_length=255, blank=True, null=True)
    is_sold = models.BooleanField(default=False)
    sell_price = models.IntegerField(blank=True, null=True)
    sell_description = models.CharField(max_length=255, blank=True, null=True)
    quantity_on_hand = models.IntegerField(blank=True, null=True)
    updated_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'laravel_crm_xero_items'
        ordering = ['-created_at']

    def __str__(self):
        return self.name or self.code or str(self.id)


class XeroContact(models.Model):
    """Xero contact sync mapping for organisations."""
    external_id = models.CharField(max_length=255)
    team = models.ForeignKey(
        'accounts.Team',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='xero_contacts',
        db_index=True
    )
    organisation = models.ForeignKey(
        'crm.Organisation',
        on_delete=models.CASCADE,
        related_name='xero_contacts'
    )
    contact_id = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'laravel_crm_xero_contacts'
        ordering = ['-created_at']

    def __str__(self):
        return self.name or str(self.id)


class XeroPerson(models.Model):
    """Xero contact person sync mapping."""
    external_id = models.CharField(max_length=255)
    team = models.ForeignKey(
        'accounts.Team',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='xero_people',
        db_index=True
    )
    person = models.ForeignKey(
        'crm.Person',
        on_delete=models.CASCADE,
        related_name='xero_people'
    )
    contact_id = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'laravel_crm_xero_people'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() or str(self.id)


class XeroInvoice(models.Model):
    """Xero invoice sync mapping."""
    external_id = models.CharField(max_length=255)
    team = models.ForeignKey(
        'accounts.Team',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='xero_invoices',
        db_index=True
    )
    invoice = models.ForeignKey(
        'sales.Invoice',
        on_delete=models.CASCADE,
        related_name='xero_invoices'
    )
    xero_type = models.CharField(max_length=255)
    xero_id = models.CharField(max_length=255)
    number = models.CharField(max_length=255, blank=True, null=True)
    reference = models.CharField(max_length=255, blank=True, null=True)
    subtotal = models.IntegerField(blank=True, null=True)
    total_tax = models.IntegerField(blank=True, null=True)
    total = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    amount_due = models.IntegerField(blank=True, null=True)
    amount_paid = models.IntegerField(blank=True, null=True)
    amount_credited = models.IntegerField(blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    line_amount_types = models.CharField(max_length=255, blank=True, null=True)
    currency_code = models.CharField(max_length=3, blank=True, null=True)
    fully_paid_at = models.DateTimeField(blank=True, null=True)
    xero_updated_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'laravel_crm_xero_invoices'
        ordering = ['-created_at']

    def __str__(self):
        return self.number or self.xero_id


class XeroPurchaseOrder(models.Model):
    """Xero purchase order sync mapping."""
    external_id = models.CharField(max_length=255)
    team = models.ForeignKey(
        'accounts.Team',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='xero_purchase_orders',
        db_index=True
    )
    purchase_order = models.ForeignKey(
        'purchasing.PurchaseOrder',
        on_delete=models.CASCADE,
        related_name='xero_purchase_orders'
    )
    xero_type = models.CharField(max_length=255)
    xero_id = models.CharField(max_length=255)
    number = models.CharField(max_length=255, blank=True, null=True)
    reference = models.CharField(max_length=255, blank=True, null=True)
    subtotal = models.IntegerField(blank=True, null=True)
    total_tax = models.IntegerField(blank=True, null=True)
    total = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)
    delivery_date = models.DateField(blank=True, null=True)
    line_amount_types = models.CharField(max_length=255, blank=True, null=True)
    currency_code = models.CharField(max_length=3, blank=True, null=True)
    xero_updated_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'laravel_crm_xero_purchase_orders'
        ordering = ['-created_at']

    def __str__(self):
        return self.number or self.xero_id
