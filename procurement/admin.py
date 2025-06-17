from django.contrib import admin
from .models import (
    PurchaseRequest, Quotation, PurchaseOrder, GoodsReceivedNote, SupplierPerformance,
    Asset, AssetCategory, AssetCheckout, MaintenanceRecord
)

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'status', 'purchase_date', 'current_value')
    list_filter = ('category', 'status', 'purchase_date')
    search_fields = ('name', 'category__name', 'asset_code')

@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(AssetCheckout)
class AssetCheckoutAdmin(admin.ModelAdmin):
    list_display = ('asset', 'checked_out_to', 'checked_out_date', 'expected_return_date', 'actual_return_date')
    list_filter = ('checked_out_date', 'expected_return_date', 'actual_return_date')
    search_fields = ('asset__name', 'checked_out_to', 'purpose')

@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ('asset', 'maintenance_date', 'maintenance_type', 'cost', 'performed_by')
    list_filter = ('maintenance_date', 'maintenance_type')
    search_fields = ('asset__name', 'description', 'performed_by')

@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'requester', 'department', 'status', 'date_created')
    list_filter = ('status', 'department', 'date_created')
    search_fields = ('title', 'requester', 'department')

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ('supplier_name', 'price', 'request')
    list_filter = ('supplier_name',)
    search_fields = ('supplier_name', 'request__title')

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'total_amount', 'status', 'date_created')
    list_filter = ('status', 'date_created')
    search_fields = ('supplier', 'request__title')

@admin.register(GoodsReceivedNote)
class GoodsReceivedNoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'purchase_order', 'received_by', 'date_received')
    list_filter = ('date_received',)
    search_fields = ('purchase_order__supplier', 'received_by')

@admin.register(SupplierPerformance)
class SupplierPerformanceAdmin(admin.ModelAdmin):
    list_display = ('supplier_name', 'rating', 'review_date')
    list_filter = ('rating', 'review_date')
    search_fields = ('supplier_name', 'comments')
