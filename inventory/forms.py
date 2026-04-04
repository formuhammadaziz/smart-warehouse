from django import forms
from .models import Product, Category, WarehouseLocation, RawMaterial, BillOfMaterials, InventoryTransaction


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class WarehouseLocationForm(forms.ModelForm):
    class Meta:
        model = WarehouseLocation
        fields = ['name', 'code', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'sku', 'category', 'unit', 'minimum_stock', 'current_stock', 'default_location', 'description']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'current_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'default_location': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class RawMaterialForm(forms.ModelForm):
    class Meta:
        model = RawMaterial
        fields = ['name', 'code', 'unit', 'current_stock', 'minimum_stock', 'location', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'current_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.001'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.001'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class BOMForm(forms.ModelForm):
    class Meta:
        model = BillOfMaterials
        fields = ['product', 'raw_material', 'quantity_required', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'raw_material': forms.Select(attrs={'class': 'form-select'}),
            'quantity_required': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.0001'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class StockTransactionForm(forms.ModelForm):
    class Meta:
        model = InventoryTransaction
        fields = ['product', 'raw_material', 'quantity', 'transaction_type', 'warehouse_location', 'destination_location', 'reference', 'notes', 'date']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'raw_material': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'warehouse_location': forms.Select(attrs={'class': 'form-select'}),
            'destination_location': forms.Select(attrs={'class': 'form-select'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned = super().clean()
        product = cleaned.get('product')
        raw_material = cleaned.get('raw_material')
        quantity = cleaned.get('quantity')
        if not product and not raw_material:
            raise forms.ValidationError('Select either a product or a raw material.')
        if product and raw_material:
            raise forms.ValidationError('Select only one: product or raw material.')
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError('Quantity must be greater than 0.')
        return cleaned
