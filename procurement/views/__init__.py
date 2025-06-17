from .general_views import UserProfileView
from .procurement_views import (
    PurchaseRequestListView, PurchaseRequestCreateView,
    PurchaseRequestDetailView, PurchaseRequestApprovalView,
    QuotationCreateView, QuotationComparisonView
)
from .asset_views import (
    AssetListView, AssetCreateView, AssetDetailView,
    AssetUpdateView, AssetCheckoutView, AssetReturnView,
    MaintenanceRecordCreateView
)
