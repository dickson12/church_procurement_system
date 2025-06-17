from django.views.generic import ListView, CreateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from ..models.procurement import (
    PurchaseRequest, Quotation, PurchaseOrder, GoodsReceivedNote
)

class PurchaseRequestListView(LoginRequiredMixin, ListView):
    model = PurchaseRequest
    template_name = 'procurement/request_list.html'
    context_object_name = 'requests'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status.upper())
        return queryset

class PurchaseRequestCreateView(LoginRequiredMixin, CreateView):
    model = PurchaseRequest
    template_name = 'procurement/request_form.html'
    fields = ['title', 'description', 'department']
    success_url = reverse_lazy('procurement:request_list')

    def form_valid(self, form):
        form.instance.requester = self.request.user.username
        return super().form_valid(form)

class PurchaseRequestDetailView(LoginRequiredMixin, DetailView):
    model = PurchaseRequest
    template_name = 'procurement/request_detail.html'
    context_object_name = 'request'

class PurchaseRequestApprovalView(LoginRequiredMixin, DetailView):
    model = PurchaseRequest
    template_name = 'procurement/request_approve.html'
    context_object_name = 'request'

    def post(self, request, *args, **kwargs):
        purchase_request = self.get_object()
        action = request.POST.get('action')
        
        if action == 'approve':
            purchase_request.approve(request.user.username)
            messages.success(request, 'Request approved successfully')
        elif action == 'reject':
            reason = request.POST.get('rejection_reason')
            purchase_request.reject(reason)
            messages.success(request, 'Request rejected')
            
        return redirect('procurement:request_detail', pk=purchase_request.pk)

class QuotationCreateView(LoginRequiredMixin, CreateView):
    model = Quotation
    template_name = 'procurement/quotation_form.html'
    fields = ['supplier_name', 'price', 'delivery_time', 'notes']
    
    def form_valid(self, form):
        request_pk = self.kwargs.get('request_pk')
        form.instance.request = get_object_or_404(PurchaseRequest, pk=request_pk)
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('procurement:request_detail', kwargs={'pk': self.kwargs['request_pk']})

class QuotationComparisonView(LoginRequiredMixin, DetailView):
    model = PurchaseRequest
    template_name = 'procurement/quotation_comparison.html'
    context_object_name = 'request'

    def post(self, request, *args, **kwargs):
        purchase_request = self.get_object()
        quotation_id = request.POST.get('quotation_id')
        selected_quotation = get_object_or_404(Quotation, pk=quotation_id)
        
        purchase_request.selected_quotation = selected_quotation
        purchase_request.status = 'QUOTATION_SELECTED'
        purchase_request.save()
        
        messages.success(request, 'Quotation selected successfully')
        return redirect('procurement:request_detail', pk=purchase_request.pk)

class SelectQuotationView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        purchase_request = get_object_or_404(PurchaseRequest, pk=kwargs['pk'])
        quotation_id = request.POST.get('quotation_id')
        
        if quotation_id:
            quotation = get_object_or_404(Quotation, pk=quotation_id)
            purchase_request.selected_quotation = quotation
            purchase_request.status = 'QUOTATION_SELECTED'
            purchase_request.save()
            messages.success(request, 'Quotation selected successfully')
        else:
            messages.error(request, 'Please select a quotation')
        
        return redirect('procurement:request_detail', pk=purchase_request.pk)
