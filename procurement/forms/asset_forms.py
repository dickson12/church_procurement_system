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
        fields = [
            'checked_out_to_name', 'checked_out_to_phone', 'department',
            'purpose', 'expected_return_date', 'condition_at_checkout',
            'checkout_notes'
        ]
        widgets = {
            'checked_out_to_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name of the person taking the asset'
            }),
            'checked_out_to_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Department or ministry'
            }),
            'purpose': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe the purpose of checking out this asset'
            }),
            'expected_return_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'min': timezone.localtime().strftime('%Y-%m-%dT%H:%M')
            }),
            'condition_at_checkout': forms.Select(attrs={
                'class': 'form-select'
            }),
            'checkout_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any additional notes about the checkout'
            })
        }

    def clean_expected_return_date(self):
        expected_return_date = self.cleaned_data.get('expected_return_date')
        if expected_return_date and timezone.localtime(expected_return_date) < timezone.localtime():
            raise forms.ValidationError('Expected return date cannot be in the past')
        return expected_return_date

    def clean_checked_out_to_phone(self):
        phone = self.cleaned_data.get('checked_out_to_phone')
        # Remove any non-digit characters
        cleaned_phone = ''.join(filter(str.isdigit, phone))
        if len(cleaned_phone) < 10:
            raise forms.ValidationError('Please enter a valid phone number')
        return cleaned_phone

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
