from django.db import models
from django.conf import settings
from django.utils import timezone
from inventory.models import Product, RawMaterial, InventoryTransaction


class ProductionOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('in_production', 'Ishlab chiqarishda'),
        ('completed', 'Yakunlangan'),
        ('cancelled', 'Bekor qilingan'),
    ]

    order_number = models.CharField(max_length=50, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='production_orders')
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='created_orders'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_orders'
    )
    planned_start = models.DateTimeField(null=True, blank=True)
    planned_end = models.DateTimeField(null=True, blank=True)
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.order_number} - {self.product.product_name}'

    @property
    def current_stage(self):
        stage = self.stages.filter(status='in_progress').first()
        if not stage:
            stage = self.stages.filter(status='pending').first()
        return stage

    @property
    def progress_percent(self):
        total = self.stages.count()
        if not total:
            return 0
        done = self.stages.filter(status='completed').count()
        return int((done / total) * 100)

    def can_start(self):
        """Check if raw materials are sufficient for this order."""
        from inventory.models import BillOfMaterials
        bom_items = BillOfMaterials.objects.filter(product=self.product)
        for item in bom_items:
            needed = item.quantity_required * self.quantity
            if item.raw_material.current_stock < needed:
                return False, item.raw_material.name
        return True, None


class ProductionStage(models.Model):
    STAGE_CHOICES = [
        ('preparation', 'Tayyorgarlik'),
        ('manufacturing', 'Ishlab chiqarish'),
        ('quality_check', 'Sifat nazorati'),
        ('packaging', 'Qadoqlash'),
        ('finished', 'Tayyor'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('in_progress', 'Jarayonda'),
        ('completed', 'Yakunlangan'),
        ('skipped', "O'tkazib yuborilgan"),
    ]

    order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name='stages')
    stage_name = models.CharField(max_length=30, choices=STAGE_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    order_index = models.PositiveSmallIntegerField(default=0)
    notes = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        ordering = ['order_index']

    def __str__(self):
        return f'{self.order.order_number} - {self.get_stage_name_display()}'
