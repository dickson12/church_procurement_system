from django import forms
from .models import PurchaseRequest, Quotation, PurchaseOrder
from django.core.exceptions import ValidationError
from django.utils import timezone

class PurchaseRequestForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        fields = ['title', 'description', 'department']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise ValidationError('Title must be at least 5 characters long')
        return title

class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ['supplier_name', 'price', 'delivery_terms', 'document'
        ]
        widgets = {
            'supplier_name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'delivery_terms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'document': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.purchase_request = kwargs.pop('purchase_request', None)
        super().__init__(*args, **kwargs)
        self.fields['supplier_name'].help_text = 'Enter the full name of the supplier'
        self.fields['delivery_terms'].help_text = 'Include delivery time, shipping terms, and other relevant details'
        self.fields['document'].help_text = 'Upload the quotation document (PDF, Word, Excel, or images)'

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise ValidationError('Price must be greater than 0')
        return price

    def clean_document(self):
        document = self.cleaned_data.get('document')
        if document:
            # Get the file extension
            ext = document.name.split('.')[-1].lower()
            allowed_extensions = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png']
            if ext not in allowed_extensions:
                raise ValidationError('Unsupported file type. Please upload PDF, Word, Excel, or image files.')
        return document

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.purchase_request:
            instance.request = self.purchase_request
        if commit:
            instance.save()
        return instance

class PurchaseOrderForm(forms.ModelForm):
    selected_quotation = forms.ModelChoiceField(
        queryset=None,
        empty_label="Select a quotation",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    negotiated_price = forms.DecimalField(
        max_digits=10, 
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'step': '0.01'
        })
    )

    class Meta:
        model = PurchaseOrder
        fields = ['terms']
        widgets = {
            'terms': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.purchase_request = kwargs.pop('purchase_request', None)
        super().__init__(*args, **kwargs)
        
        if self.purchase_request:
            self.fields['selected_quotation'].queryset = Quotation.objects.filter(
                request=self.purchase_request
            )
        
        self.fields['selected_quotation'].help_text = 'Select the quotation to base this purchase order on'
        self.fields['negotiated_price'].help_text = 'Enter the final negotiated price with the supplier'
        self.fields['terms'].help_text = 'Enter the terms and conditions for this purchase order'

    def clean(self):
        cleaned_data = super().clean()
        selected_quotation = cleaned_data.get('selected_quotation')
        negotiated_price = cleaned_data.get('negotiated_price')
        
        if selected_quotation:
            cleaned_data['supplier'] = selected_quotation.supplier_name
            cleaned_data['total_amount'] = negotiated_price
            cleaned_data['request'] = selected_quotation.request
            
        if negotiated_price and negotiated_price <= 0:
            raise ValidationError({'negotiated_price': 'Price must be greater than 0'})
            
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        selected_quotation = self.cleaned_data['selected_quotation']
        negotiated_price = self.cleaned_data['negotiated_price']
        
        instance.supplier = selected_quotation.supplier_name
        instance.total_amount = negotiated_price
        instance.request = selected_quotation.request
        
        # Store the selected quotation ID for the signal handler
        instance._selected_quotation_id = selected_quotation.id
        
        if commit:
            instance.save()
        return instance
