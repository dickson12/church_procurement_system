from django.urls import path
from . import dashboard_views
from .views.general_views import UserProfileView
from .views.procurement_views import (
    PurchaseRequestListView, PurchaseRequestCreateView,
    PurchaseRequestDetailView, PurchaseRequestApprovalView,
    QuotationCreateView, QuotationComparisonView,
    SelectQuotationView
)
from .views.asset_views import (
    AssetListView, AssetCreateView, AssetDetailView,
    AssetUpdateView, AssetCheckoutView, AssetReturnView,
    MaintenanceRecordCreateView
)

app_name = 'procurement'

urlpatterns = [
    # Dashboard
    path('', dashboard_views.DashboardView.as_view(), name='dashboard'),
    
    # User Profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # Purchase Requests
    path('requests/', PurchaseRequestListView.as_view(), name='request_list'),
    path('requests/new/', PurchaseRequestCreateView.as_view(), name='request_create'),
    path('requests/<int:pk>/', PurchaseRequestDetailView.as_view(), name='request_detail'),
    path('requests/<int:pk>/approve/', PurchaseRequestApprovalView.as_view(), name='request_approve'),
    
    # Quotations
    path('requests/<int:request_pk>/quotation/add/', QuotationCreateView.as_view(), name='quotation_create'),
    path('requests/<int:pk>/compare/', QuotationComparisonView.as_view(), name='quotation_comparison'),
    path('requests/<int:pk>/select-quotation/', SelectQuotationView.as_view(), name='select_quotation'),
    
    # Assets
    path('assets/', AssetListView.as_view(), name='asset_list'),
    path('assets/add/', AssetCreateView.as_view(), name='asset_create'),
    path('assets/<int:pk>/', AssetDetailView.as_view(), name='asset_detail'),
    path('assets/<int:pk>/edit/', AssetUpdateView.as_view(), name='asset_update'),
    path('assets/<int:pk>/checkout/', AssetCheckoutView.as_view(), name='asset_checkout'),
    path('assets/<int:pk>/return/', AssetReturnView.as_view(), name='asset_return'),
    path('assets/<int:pk>/maintenance/add/', MaintenanceRecordCreateView.as_view(), name='maintenance_create'),
]
