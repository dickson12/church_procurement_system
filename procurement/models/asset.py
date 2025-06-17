from django.db import models
from django.conf import settings
from django.utils import timezone

class AssetCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Asset Categories"

class Asset(models.Model):
    CONDITION_CHOICES = [
        ('EXCELLENT', 'Excellent'),
        ('GOOD', 'Good'),
        ('FAIR', 'Fair'),
        ('POOR', 'Poor'),
        ('DAMAGED', 'Damaged'),
    ]

    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('CHECKED_OUT', 'Checked Out'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('RETIRED', 'Retired'),
    ]

    name = models.CharField(max_length=200)
    asset_code = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT)
    description = models.TextField()
    purchase_date = models.DateField()
    purchase_value = models.DecimalField(max_digits=10, decimal_places=2)
    current_value = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    location = models.CharField(max_length=100)
    last_maintained = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.asset_code} - {self.name}"

class AssetCheckout(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT)
    # Person checking out the asset
    checked_out_to_name = models.CharField(max_length=100)
    checked_out_to_phone = models.CharField(max_length=20)
    department = models.CharField(max_length=100)
    # Checkout details
    purpose = models.TextField()
    checked_out_date = models.DateTimeField(default=timezone.now)
    expected_return_date = models.DateTimeField()
    actual_return_date = models.DateTimeField(null=True, blank=True)
    # Condition tracking
    condition_at_checkout = models.CharField(max_length=20, choices=Asset.CONDITION_CHOICES)
    condition_at_return = models.CharField(max_length=20, choices=Asset.CONDITION_CHOICES, null=True, blank=True)
    # Notes
    checkout_notes = models.TextField(blank=True)
    return_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.asset} - {self.checked_out_to_name} - {self.checked_out_date.date()}"

    def is_overdue(self):
        if not self.actual_return_date and timezone.now() > self.expected_return_date:
            return True
        return False

class MaintenanceRecord(models.Model):
    MAINTENANCE_TYPE_CHOICES = [
        ('ROUTINE', 'Routine Maintenance'),
        ('REPAIR', 'Repair'),
        ('INSPECTION', 'Inspection'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.PROTECT)
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES)
    maintenance_date = models.DateField()
    performed_by = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField()
    next_maintenance_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.asset} - {self.maintenance_type} - {self.maintenance_date}"
