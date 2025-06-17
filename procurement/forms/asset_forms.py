from django import forms
from django.utils import timezone
from ..models.asset import Asset, AssetCategory, AssetCheckout, MaintenanceRecord

class AssetCategoryForm(forms.ModelForm):
    class Meta:
        model = AssetCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'name', 'asset_code', 'category', 'description',
            'purchase_date', 'purchase_value', 'current_value',
            'condition', 'status', 'location', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'asset_code': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'purchase_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'current_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        purchase_value = cleaned_data.get('purchase_value')
        current_value = cleaned_data.get('current_value')
        purchase_date = cleaned_data.get('purchase_date')

        if purchase_value and current_value and purchase_value < current_value:
            self.add_error('current_value', 'Current value cannot be greater than purchase value')

        if purchase_date and purchase_date > timezone.now().date():
            self.add_error('purchase_date', 'Purchase date cannot be in the future')

        return cleaned_data

class AssetCheckoutForm(forms.ModelForm):
    class Meta:
        model = AssetCheckout
        fields = ['asset', 'checked_out_by', 'department', 'purpose', 
                 'expected_return_date', 'condition_at_checkout', 'checkout_notes']
        widgets = {
            'asset': forms.Select(attrs={'class': 'form-select'}),
            'checked_out_by': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'expected_return_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'condition_at_checkout': forms.Select(attrs={'class': 'form-select'}),
            'checkout_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available assets in the dropdown
        self.fields['asset'].queryset = Asset.objects.filter(status='AVAILABLE')

class AssetReturnForm(forms.ModelForm):
    class Meta:
        model = AssetCheckout
        fields = ['condition_at_return', 'return_notes']
        widgets = {
            'condition_at_return': forms.Select(attrs={'class': 'form-select'}),
            'return_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class MaintenanceRecordForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = ['maintenance_type', 'maintenance_date', 'performed_by', 'cost',
                 'description', 'next_maintenance_date']
        widgets = {
            'maintenance_type': forms.Select(attrs={'class': 'form-select'}),
            'maintenance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'performed_by': forms.TextInput(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'next_maintenance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
