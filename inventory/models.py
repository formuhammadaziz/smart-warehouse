from django.db import models
from django.conf import settings
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class WarehouseLocation(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.code})'


class Product(models.Model):
    UNIT_CHOICES = [
        ('pcs', 'Pieces'),
        ('kg', 'Kilograms'),
        ('g', 'Grams'),
        ('l', 'Liters'),
        ('ml', 'Milliliters'),
        ('m', 'Meters'),
        ('m2', 'Square Meters'),
        ('m3', 'Cubic Meters'),
        ('box', 'Box'),
        ('pack', 'Pack'),
    ]

    product_name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True, verbose_name='SKU')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='pcs')
    minimum_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    default_location = models.ForeignKey(WarehouseLocation, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['product_name']

    def __str__(self):
        return f'{self.product_name} ({self.sku})'

    @property
    def is_low_stock(self):
        return self.current_stock <= self.minimum_stock

    @property
    def stock_status(self):
        if self.current_stock == 0:
            return 'out_of_stock'
        elif self.is_low_stock:
            return 'low'
        return 'ok'


class RawMaterial(models.Model):
    UNIT_CHOICES = Product.UNIT_CHOICES

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='kg')
    current_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    minimum_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    location = models.ForeignKey(WarehouseLocation, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.code})'

    @property
    def is_low_stock(self):
        return self.current_stock <= self.minimum_stock


class BillOfMaterials(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bom_items')
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name='bom_items')
    quantity_required = models.DecimalField(max_digits=12, decimal_places=4)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('product', 'raw_material')
        verbose_name = 'Bill of Materials'
        verbose_name_plural = 'Bills of Materials'

    def __str__(self):
        return f'{self.product.product_name} → {self.raw_material.name} x{self.quantity_required}'


class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('TRANSFER', 'Transfer'),
        ('ADJUSTMENT', 'Adjustment'),
        ('PRODUCTION', 'Production Consumption'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=15, choices=TRANSACTION_TYPES)
    warehouse_location = models.ForeignKey(WarehouseLocation, on_delete=models.SET_NULL, null=True, blank=True)
    destination_location = models.ForeignKey(WarehouseLocation, on_delete=models.SET_NULL, null=True, blank=True, related_name='incoming_transactions')
    reference = models.CharField(max_length=100, blank=True, help_text='Order/Invoice reference')
    notes = models.TextField(blank=True)
    date = models.DateTimeField(default=timezone.now)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        item = self.product or self.raw_material
        return f'{self.transaction_type} - {item} - {self.quantity}'
