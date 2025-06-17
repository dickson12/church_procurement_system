from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum

from ..models.asset import Asset, AssetCategory, AssetCheckout, MaintenanceRecord
from ..forms.asset_forms import (
    AssetForm, AssetCategoryForm, AssetCheckoutForm,
    AssetReturnForm, MaintenanceRecordForm
)

class AssetListView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'procurement/asset/asset_list.html'
    context_object_name = 'assets'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_value'] = Asset.objects.exclude(status='RETIRED').aggregate(
            total=Sum('current_value')
        )['total'] or 0
        return context

class AssetCreateView(LoginRequiredMixin, CreateView):
    model = Asset
    form_class = AssetForm
    template_name = 'procurement/asset/asset_form.html'
    success_url = reverse_lazy('procurement:asset_list')

    def form_valid(self, form):
        messages.success(self.request, 'Asset created successfully!')
        return super().form_valid(form)

class AssetDetailView(LoginRequiredMixin, DetailView):
    model = Asset
    template_name = 'procurement/asset/asset_detail.html'
    context_object_name = 'asset'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all checkouts ordered by date
        context['checkouts'] = self.object.assetcheckout_set.all().order_by('-checked_out_date')
        
        # Get maintenance records
        context['maintenance_records'] = self.object.maintenancerecord_set.all().order_by('-maintenance_date')
        
        # Get current checkout if asset is checked out
        if self.object.status == 'CHECKED_OUT':
            try:
                context['current_checkout'] = self.object.assetcheckout_set.filter(
                    actual_return_date__isnull=True
                ).latest('checked_out_date')
            except AssetCheckout.DoesNotExist:
                context['current_checkout'] = None
        
        return context

class AssetUpdateView(LoginRequiredMixin, UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = 'procurement/asset/asset_form.html'
    
    def get_success_url(self):
        return reverse_lazy('procurement:asset_detail', kwargs={'pk': self.object.pk})

class AssetCheckoutView(LoginRequiredMixin, CreateView):
    model = AssetCheckout
    form_class = AssetCheckoutForm
    template_name = 'procurement/asset/asset_checkout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asset'] = self.get_asset()
        return context

    def get_asset(self):
        return get_object_or_404(Asset, pk=self.kwargs['pk'])

    def form_valid(self, form):
        checkout = form.save(commit=False)
        checkout.asset = self.get_asset()
        checkout.checked_out_to = self.request.user.username
        
        if checkout.asset.status != 'AVAILABLE':
            messages.error(self.request, 'This asset is not available for checkout')
            return self.form_invalid(form)

        # Update asset status and save checkout
        checkout.asset.status = 'CHECKED_OUT'
        checkout.asset.save()
        messages.success(self.request, f'Asset {checkout.asset.name} has been checked out successfully!')
        
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('procurement:asset_detail', kwargs={'pk': self.object.asset.pk})

class AssetReturnView(LoginRequiredMixin, UpdateView):
    model = AssetCheckout
    form_class = AssetReturnForm
    template_name = 'procurement/asset/asset_return.html'
    
    def form_valid(self, form):
        checkout = form.save(commit=False)
        checkout.actual_return_date = timezone.now()
        checkout.save()
        
        # Update asset status and condition
        asset = checkout.asset
        asset.status = 'AVAILABLE'
        asset.condition = checkout.condition_at_return
        asset.save()
        
        messages.success(self.request, f'Asset {asset.name} has been returned successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('procurement:asset_detail', kwargs={'pk': self.object.asset.pk})

class MaintenanceRecordCreateView(LoginRequiredMixin, CreateView):
    model = MaintenanceRecord
    form_class = MaintenanceRecordForm
    template_name = 'procurement/asset/maintenance_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asset'] = get_object_or_404(Asset, pk=self.kwargs['asset_pk'])
        return context

    def form_valid(self, form):
        maintenance = form.save(commit=False)
        maintenance.asset = get_object_or_404(Asset, pk=self.kwargs['asset_pk'])
        
        # Update asset's last maintenance date
        asset = maintenance.asset
        asset.last_maintained = maintenance.maintenance_date
        asset.save()
        
        messages.success(self.request, 'Maintenance record added successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('procurement:asset_detail', kwargs={'pk': self.kwargs['asset_pk']})
