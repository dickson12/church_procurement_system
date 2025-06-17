from django.urls import path
from . import views, dashboard_views

app_name = 'procurement'

urlpatterns = [
    path('', dashboard_views.DashboardView.as_view(), name='dashboard'),
    path('requests/', views.PurchaseRequestListView.as_view(), name='request_list'),
    path('requests/new/', views.PurchaseRequestCreateView.as_view(), name='request_create'),
    path('requests/<int:pk>/', views.PurchaseRequestDetailView.as_view(), name='request_detail'),
    path('requests/<int:pk>/approve/', views.PurchaseRequestApprovalView.as_view(), name='request_approve'),
    path('requests/<int:request_pk>/quotation/add/', views.QuotationCreateView.as_view(), name='quotation_create'),
    path('requests/<int:pk>/compare/', views.QuotationComparisonView.as_view(), name='quotation_comparison'),
    path('requests/<int:pk>/select-quotation/', views.SelectQuotationView.as_view(), name='select_quotation'),
    path('requests/<int:request_pk>/po/create/', views.PurchaseOrderCreateView.as_view(), name='po_create'),
    path('po/<int:po_pk>/receive/', views.GoodsReceivedCreateView.as_view(), name='grn_create'),
    
    # Export URLs
    path('export/requests/csv/', dashboard_views.export_purchase_requests_csv, name='export_requests_csv'),
    path('export/supplier-performance/pdf/', dashboard_views.export_supplier_performance_pdf, name='supplier_performance_pdf'),
    path('po/<int:po_id>/pdf/', dashboard_views.generate_purchase_order_pdf, name='po_pdf'),
]
