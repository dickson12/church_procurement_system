from django.contrib import admin
from .models import (
    PurchaseRequest,
    Quotation,
    PurchaseOrder,
    GoodsReceivedNote,
    SupplierPerformance
)

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
    search_fields = ('received_by', 'purchase_order__supplier')

@admin.register(SupplierPerformance)
class SupplierPerformanceAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'score', 'date_evaluated')
    list_filter = ('score', 'date_evaluated')
    search_fields = ('supplier', 'comments')
