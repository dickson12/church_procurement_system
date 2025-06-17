from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from model_utils import FieldTracker

class PurchaseRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('QUOTATION_SELECTED', 'Quotation Selected'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed')
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    requester = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    date_created = models.DateTimeField(auto_now_add=True)
    rejection_reason = models.TextField(blank=True, null=True)
    approved_by = models.CharField(max_length=100, blank=True, null=True)
    approved_date = models.DateTimeField(null=True, blank=True)
    selected_quotation = models.ForeignKey('Quotation', null=True, blank=True, on_delete=models.SET_NULL, related_name='selected_for_requests')

    tracker = FieldTracker(fields=['status'])

    def __str__(self):
        return f"{self.title} - {self.status}"

    def approve(self, approved_by):
        """Approve the purchase request"""
        if self.status != 'PENDING':
            raise ValidationError("Only pending requests can be approved")
        
        self.status = 'APPROVED'
        self.approved_by = approved_by
        self.approved_date = timezone.now()
        self.save()

    def reject(self, reason):
        """Reject the purchase request with a reason"""
        if self.status != 'PENDING':
            raise ValidationError("Only pending requests can be rejected")
        
        self.status = 'REJECTED'
        self.rejection_reason = reason
        self.save()

class Quotation(models.Model):
    supplier_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_terms = models.TextField()
    request = models.ForeignKey(PurchaseRequest, on_delete=models.CASCADE, related_name='quotations')
    document = models.FileField(upload_to='quotations/', null=True, blank=True)
    is_selected = models.BooleanField(default=False)
    submission_date = models.DateTimeField(default=timezone.now)
    validity_period = models.IntegerField(default=30, help_text="Validity period in days")

    def __str__(self):
        return f"{self.supplier_name} - ${self.price}"

    def is_valid(self):
        """Check if the quotation is still valid based on validity period"""
        return timezone.now() <= self.submission_date + timezone.timedelta(days=self.validity_period)

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled')
    ]
    
    request = models.ForeignKey(PurchaseRequest, on_delete=models.CASCADE, related_name='purchase_orders')
    supplier = models.CharField(max_length=200)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    terms = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    date_created = models.DateTimeField(auto_now_add=True)
    expected_delivery_date = models.DateTimeField(null=True, blank=True)
    actual_delivery_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"PO-{self.id} - {self.supplier}"

    def cancel(self, reason):
        """Cancel the purchase order with a reason"""
        if self.status == 'DELIVERED':
            raise ValidationError("Cannot cancel a delivered order")
        
        self.status = 'CANCELLED'
        self.save()
        
        # Revert request status
        self.request.status = 'APPROVED'
        self.request.save()

class GoodsReceivedNote(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    received_by = models.CharField(max_length=100)
    date_received = models.DateTimeField()
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"GRN-{self.id} for {self.purchase_order}"

class SupplierPerformance(models.Model):
    supplier_name = models.CharField(max_length=200)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1 to 5 rating
    comments = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.supplier_name} - Rating: {self.rating}"

    class Meta:
        ordering = ['-review_date']
