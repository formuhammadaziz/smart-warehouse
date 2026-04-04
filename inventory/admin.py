from django.contrib import admin
from .models import Category, WarehouseLocation, Product, RawMaterial, BillOfMaterials, InventoryTransaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(WarehouseLocation)
class WarehouseLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    list_filter = ('is_active',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'sku', 'category', 'unit', 'current_stock', 'minimum_stock', 'is_low_stock')
    list_filter = ('category', 'unit')
    search_fields = ('product_name', 'sku')


@admin.register(RawMaterial)
class RawMaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'unit', 'current_stock', 'minimum_stock')
    search_fields = ('name', 'code')


@admin.register(BillOfMaterials)
class BOMAdmin(admin.ModelAdmin):
    list_display = ('product', 'raw_material', 'quantity_required')


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'product', 'raw_material', 'quantity', 'date', 'performed_by')
    list_filter = ('transaction_type', 'date')
    search_fields = ('product__product_name', 'raw_material__name', 'reference')
