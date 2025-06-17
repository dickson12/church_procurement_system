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
    INSPECTION_STATUS_CHOICES = [
        ('PENDING', 'Pending Inspection'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('PARTIALLY_ACCEPTED', 'Partially Accepted')
    ]

    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='goods_received_notes')
    received_by = models.CharField(max_length=100)
    date_received = models.DateTimeField()
    remarks = models.TextField(blank=True)
    inspection_status = models.CharField(
        max_length=20,
        choices=INSPECTION_STATUS_CHOICES,
        default='PENDING'
    )
    inspection_date = models.DateTimeField(null=True, blank=True)
    inspector = models.CharField(max_length=100, null=True, blank=True)
    inspection_notes = models.TextField(blank=True)
    rejection_reasons = models.TextField(blank=True)

    def __str__(self):
        return f"GRN-{self.id} - {self.purchase_order}"

    def accept_delivery(self, inspector):
        """Mark the delivery as accepted after inspection"""
        self.inspection_status = 'ACCEPTED'
        self.inspection_date = timezone.now()
        self.inspector = inspector
        self.save()

    def reject_delivery(self, inspector, reasons):
        """Reject the delivery with reasons"""
        self.inspection_status = 'REJECTED'
        self.inspection_date = timezone.now()
        self.inspector = inspector
        self.rejection_reasons = reasons
        self.save()

    def partial_accept(self, inspector, notes):
        """Mark delivery as partially accepted with notes"""
        self.inspection_status = 'PARTIALLY_ACCEPTED'
        self.inspection_date = timezone.now()
        self.inspector = inspector
        self.inspection_notes = notes
        self.save()

class SupplierPerformance(models.Model):
    supplier = models.CharField(max_length=200)
    score = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 rating
    comments = models.TextField()
    date_evaluated = models.DateTimeField(auto_now_add=True)
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.SET_NULL,
        null=True,
        related_name='performance_evaluations'
    )
    evaluator = models.CharField(max_length=100)
    delivery_timeliness = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    quality_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    communication_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])

    def __str__(self):
        return f"{self.supplier} - Score: {self.score}"

    def calculate_overall_score(self):
        """Calculate the overall score based on different criteria"""
        weights = {
            'delivery': 0.3,
            'quality': 0.4,
            'communication': 0.3
        }
        
        weighted_score = (
            self.delivery_timeliness * weights['delivery'] +
            self.quality_rating * weights['quality'] +
            self.communication_rating * weights['communication']
        )
        
        self.score = round(weighted_score)
        self.save()
