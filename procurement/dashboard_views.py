from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Avg, Q
from django.http import HttpResponse
from datetime import datetime
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

from .models import (
    PurchaseRequest,
    Quotation,
    PurchaseOrder,
    GoodsReceivedNote,
    SupplierPerformance
)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'procurement/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Pending requests
        context['pending_requests'] = PurchaseRequest.objects.prefetch_related('purchase_orders').filter(
            status='PENDING'
        ).order_by('-date_created')
        
        # Requests with quotations
        context['requests_with_quotations'] = PurchaseRequest.objects.prefetch_related('purchase_orders').annotate(
            quotation_count=Count('quotations')
        ).filter(
            quotation_count__gt=0,
            status='APPROVED'
        ).order_by('-date_created')
        
        # Orders awaiting delivery
        context['pending_orders'] = PurchaseOrder.objects.filter(
            status='APPROVED'
        ).order_by('-date_created')
        
        # All requests grouped by status
        context['all_requests'] = {
            'pending': PurchaseRequest.objects.prefetch_related('purchase_orders').filter(status='PENDING').order_by('-date_created'),
            'approved': PurchaseRequest.objects.prefetch_related('purchase_orders').filter(status='APPROVED').order_by('-date_created'),
            'rejected': PurchaseRequest.objects.prefetch_related('purchase_orders').filter(status='REJECTED').order_by('-date_created'),
            'in_progress': PurchaseRequest.objects.prefetch_related('purchase_orders').filter(status='IN_PROGRESS').order_by('-date_created'),
            'completed': PurchaseRequest.objects.prefetch_related('purchase_orders').filter(status='COMPLETED').order_by('-date_created'),
        }
        
        # Top suppliers (keep limited to top 10)
        context['top_suppliers'] = SupplierPerformance.objects.values(
            'supplier_name'
        ).annotate(
            avg_rating=Avg('rating')
        ).order_by('-avg_rating')[:10]
        
        # Statistics
        context['stats'] = {
            'total_requests': PurchaseRequest.objects.count(),
            'pending_approval': PurchaseRequest.objects.filter(status='PENDING').count(),
            'active_orders': PurchaseOrder.objects.exclude(status__in=['DELIVERED', 'CANCELLED']).count(),
            'completed_orders': PurchaseOrder.objects.filter(status='DELIVERED').count(),
        }
        
        return context

def export_purchase_requests_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="purchase_requests.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Title', 'Requester', 'Department', 'Status', 'Date Created', 'Approved By', 'Approved Date'])
    
    requests = PurchaseRequest.objects.all().order_by('-date_created')
    
    for pr in requests:
        writer.writerow([
            pr.title,
            pr.requester,
            pr.department,
            pr.status,
            pr.date_created,
            pr.approved_by or '',
            pr.approved_date or ''
        ])
    
    return response

def export_supplier_performance_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="supplier_performance.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    
    # Title
    styles = getSampleStyleSheet()
    elements.append(Paragraph('Supplier Performance Report', styles['Title']))
    elements.append(Paragraph('Generated on: ' + datetime.now().strftime('%Y-%m-%d'), styles['Normal']))
    
    # Data
    data = [['Supplier', 'Average Score', 'Delivery', 'Quality', 'Communication', 'Orders']]
    
    suppliers = SupplierPerformance.objects.values(
        'supplier'
    ).annotate(
        avg_score=Avg('score'),
        avg_delivery=Avg('delivery_timeliness'),
        avg_quality=Avg('quality_rating'),
        avg_communication=Avg('communication_rating'),
        total_orders=Count('purchase_order')
    ).order_by('-avg_score')
    
    for supplier in suppliers:
        data.append([
            supplier['supplier'],
            f"{supplier['avg_score']:.2f}",
            f"{supplier['avg_delivery']:.2f}",
            f"{supplier['avg_quality']:.2f}",
            f"{supplier['avg_communication']:.2f}",
            supplier['total_orders']
        ])
    
    # Create table
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(t)
    doc.build(elements)
    
    return response

def generate_purchase_order_pdf(request, po_id):
    po = PurchaseOrder.objects.get(pk=po_id)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="PO-{po.id}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    
    # Header
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f'Purchase Order #{po.id}', styles['Title']))
    elements.append(Paragraph(f'Date: {po.date_created.strftime("%Y-%m-%d")}', styles['Normal']))
    elements.append(Paragraph(f'Supplier: {po.supplier}', styles['Normal']))
    
    # PO Details
    data = [
        ['Request Title', po.request.title],
        ['Total Amount', f"${po.total_amount}"],
        ['Status', po.status],
        ['Terms', po.terms],
        ['Expected Delivery', po.expected_delivery_date.strftime('%Y-%m-%d') if po.expected_delivery_date else 'Not specified']
    ]
    
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(t)
    doc.build(elements)
    
    return response
