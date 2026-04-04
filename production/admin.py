from django.contrib import admin
from .models import ProductionOrder, ProductionStage


class ProductionStageInline(admin.TabularInline):
    model = ProductionStage
    extra = 0


@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'product', 'quantity', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'product__product_name')
    inlines = [ProductionStageInline]


@admin.register(ProductionStage)
class ProductionStageAdmin(admin.ModelAdmin):
    list_display = ('order', 'stage_name', 'status', 'performed_by', 'completed_at')
    list_filter = ('stage_name', 'status')
