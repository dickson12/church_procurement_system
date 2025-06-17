from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone

from .models import (
    PurchaseRequest, 
    Quotation, 
    PurchaseOrder,
    GoodsReceivedNote,
    SupplierPerformance
)
from .forms import PurchaseRequestForm, QuotationForm, PurchaseOrderForm

class ManagementRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Management').exists()
    
    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to perform this action. Only Management group members can approve/reject requests.')
        return redirect('procurement:request_list')

class PurchaseRequestListView(LoginRequiredMixin, ListView):
    model = PurchaseRequest
    template_name = 'procurement/request_list.html'
    context_object_name = 'requests'
    ordering = ['-date_created']

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('purchase_orders')
        if not self.request.user.groups.filter(name='Management').exists():
            # Regular users can only see their own requests
            queryset = queryset.filter(requester=self.request.user.get_full_name())
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_approve'] = self.request.user.groups.filter(name='Management').exists()
        return context

class PurchaseRequestCreateView(LoginRequiredMixin, CreateView):
    model = PurchaseRequest
    form_class = PurchaseRequestForm
    template_name = 'procurement/request_form.html'
    success_url = reverse_lazy('procurement:request_list')

    def form_valid(self, form):
        form.instance.requester = f"{self.request.user.first_name} {self.request.user.last_name}".strip() or self.request.user.username
        response = super().form_valid(form)
        messages.success(self.request, 'Purchase request created successfully!')
        return response

class PurchaseRequestDetailView(LoginRequiredMixin, DetailView):
    model = PurchaseRequest
    template_name = 'procurement/request_detail.html'
    context_object_name = 'request'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quotations'] = self.object.quotations.all()
        context['purchase_orders'] = self.object.purchase_orders.all().order_by('-date_created')
        context['can_approve'] = self.request.user.groups.filter(name='Management').exists()
        return context

class PurchaseRequestApprovalView(ManagementRequiredMixin, UpdateView):
    model = PurchaseRequest
    template_name = 'procurement/request_approve.html'
    fields = ['status']
    success_url = reverse_lazy('procurement:request_list')

    def form_valid(self, form):
        if not self.request.user.groups.filter(name='Management').exists():
            messages.error(self.request, 'You do not have permission to perform this action.')
            return redirect('procurement:request_list')
            
        status = form.cleaned_data['status']
        request = form.save(commit=False)
        
        if status == 'APPROVED':
            request.approved_by = self.request.user.get_full_name() or self.request.user.username
            request.approved_date = timezone.now()
        elif status == 'REJECTED':
            request.rejection_reason = self.request.POST.get('rejection_reason', '')
            
        request.save()
        
        action = 'approved' if status == 'APPROVED' else 'rejected'
        messages.success(self.request, f'Purchase request {request.title} has been {action}')
        return redirect(self.success_url)

class QuotationCreateView(LoginRequiredMixin, CreateView):
    model = Quotation
    form_class = QuotationForm
    template_name = 'procurement/quotation_form.html'

    def get_success_url(self):
        return reverse('procurement:request_detail', kwargs={'pk': self.object.request.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['purchase_request'] = get_object_or_404(PurchaseRequest, pk=self.kwargs['request_pk'])
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Quotation added successfully!')
        return super().form_valid(form)

class QuotationComparisonView(LoginRequiredMixin, DetailView):
    model = PurchaseRequest
    template_name = 'procurement/quotation_comparison.html'
    context_object_name = 'request'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quotations'] = self.object.quotations.all().order_by('price')
        return context

class PurchaseOrderCreateView(LoginRequiredMixin, CreateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'procurement/purchase_order_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['purchase_request'] = get_object_or_404(PurchaseRequest, pk=self.kwargs['request_pk'])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['purchase_request'] = get_object_or_404(PurchaseRequest, pk=self.kwargs['request_pk'])
        return context

    def form_valid(self, form):
        po = form.save()

        # Update the request status when PO is created
        po.request.status = 'IN_PROGRESS'
        po.request.save()

        messages.success(self.request, 'Purchase order created successfully!')
        return redirect('procurement:request_detail', pk=po.request.pk)

class GoodsReceivedCreateView(LoginRequiredMixin, CreateView):
    model = GoodsReceivedNote
    template_name = 'procurement/grn_form.html'
    fields = ['received_by', 'date_received', 'remarks']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['purchase_order'] = get_object_or_404(PurchaseOrder, pk=self.kwargs['po_pk'])
        return context

    def form_valid(self, form):
        form.instance.purchase_order = get_object_or_404(PurchaseOrder, pk=self.kwargs['po_pk'])
        form.instance.received_by = self.request.user.get_full_name()
        response = super().form_valid(form)
        
        # Update PO status
        po = form.instance.purchase_order
        po.status = 'DELIVERED'
        po.save()
        
        # Update request status
        po.request.status = 'COMPLETED'
        po.request.save()
        
        messages.success(self.request, 'Goods received note created successfully!')
        return response

    def get_success_url(self):
        return reverse('procurement:request_detail', 
                      kwargs={'pk': self.object.purchase_order.request.pk})

class SelectQuotationView(LoginRequiredMixin, View):
    def post(self, request, pk):
        purchase_request = get_object_or_404(PurchaseRequest, pk=pk)
        quotation_id = request.POST.get('quotation_id')
        
        if not quotation_id:
            messages.error(request, 'Please select a quotation.')
            return redirect('procurement:quotation_comparison', pk=pk)
            
        try:
            quotation = Quotation.objects.get(id=quotation_id, request=purchase_request)
            purchase_request.selected_quotation = quotation
            purchase_request.status = 'QUOTATION_SELECTED'
            purchase_request.save()
            
            messages.success(request, 'Quotation selected successfully!')
            return redirect('procurement:request_detail', pk=pk)
            
        except Quotation.DoesNotExist:
            messages.error(request, 'Invalid quotation selected.')
            return redirect('procurement:quotation_comparison', pk=pk)
