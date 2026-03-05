from django.db import models


class TaxRate(models.Model):
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    rate = models.DecimalField(max_digits=12, decimal_places=2)
    default = models.BooleanField(default=False)
    tax_type = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'tax_rates'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.rate}%)"


class ProductCategory(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'product_categories'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Product(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, null=True, blank=True)
    barcode = models.CharField(max_length=255, null=True, blank=True)
    sales_account = models.CharField(max_length=255, null=True, blank=True)
    purchase_account = models.CharField(max_length=255, null=True, blank=True)
    unit = models.CharField(max_length=255, null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tax_rate_ref = models.ForeignKey(
        TaxRate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    product_category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        db_index=True
    )
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    user_created = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products_created'
    )
    user_updated = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products_updated'
    )
    user_deleted = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products_deleted'
    )
    user_restored = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products_restored'
    )
    user_owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products_owned'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'products'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ProductVariation(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variations',
        db_index=True
    )
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'product_variations'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} - {self.name}"


class ProductPrice(models.Model):
    external_id = models.CharField(max_length=255)
    team_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='prices',
        db_index=True
    )
    product_variation = models.ForeignKey(
        ProductVariation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='prices',
        db_index=True
    )
    unit_price = models.IntegerField(null=True, blank=True)
    cost_per_unit = models.IntegerField(null=True, blank=True)
    direct_cost = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'product_prices'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} - {self.currency} {self.unit_price}"
