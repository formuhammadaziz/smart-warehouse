from django import forms
from .models import ProductionOrder, ProductionStage


class ProductionOrderForm(forms.ModelForm):
    class Meta:
        model = ProductionOrder
        fields = ['order_number', 'product', 'quantity', 'assigned_to', 'planned_start', 'planned_end', 'notes']
        widgets = {
            'order_number': forms.TextInput(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': '0.01'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'planned_start': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'planned_end': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        planned_start = cleaned_data.get('planned_start')
        planned_end = cleaned_data.get('planned_end')
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError('Quantity must be greater than 0.')
        if planned_start and planned_end and planned_end <= planned_start:
            raise forms.ValidationError('Planned end date must be after planned start date.')
        return cleaned_data


class ProductionStageForm(forms.ModelForm):
    class Meta:
        model = ProductionStage
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
