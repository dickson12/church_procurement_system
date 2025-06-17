from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import Group
from django.db.models import Q
from .models import PurchaseRequest, Quotation, PurchaseOrder, GoodsReceivedNote

@receiver(post_save, sender=PurchaseRequest)
def handle_request_status_change(sender, instance, created, **kwargs):
    """Handle notifications and related updates when request status changes"""
    if not created and instance.tracker.has_changed('status'):
        old_status = instance.tracker.previous('status')
        new_status = instance.status

        # Get procurement team members (users in Procurement group)
        procurement_group = Group.objects.get(name='Procurement')
        procurement_emails = [
            user.email for user in procurement_group.user_set.all()
        ]

        # Send notifications based on status changes
        if new_status == 'APPROVED':
            if procurement_emails:
                send_mail(
                    subject=f'Purchase Request {instance.id} Approved',
                    message=f'Purchase request "{instance.title}" has been approved and requires quotations.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=procurement_emails,
                    fail_silently=True,
                )

@receiver(post_save, sender=PurchaseOrder)
def handle_purchase_order_creation(sender, instance, created, **kwargs):
    """Update related quotations and request when PO is created"""
    if created:
        # Get the selected quotation from the form data stored in the instance
        if hasattr(instance, '_selected_quotation_id'):
            try:
                selected_quotation = instance.request.quotations.get(
                    id=instance._selected_quotation_id
                )
                
                # Mark the selected quotation as chosen
                selected_quotation.is_selected = True
                selected_quotation.save()
                
                # Mark other quotations as not selected
                instance.request.quotations.exclude(id=selected_quotation.id).update(
                    is_selected=False
                )
            except Quotation.DoesNotExist:
                pass  # Handle silently since this is a post-save operation

@receiver(pre_save, sender=GoodsReceivedNote)
def handle_grn_status_change(sender, instance, **kwargs):
    """Update PO status when GRN inspection status changes"""
    if instance.pk:  # Only for existing GRNs
        old_instance = GoodsReceivedNote.objects.get(pk=instance.pk)
        if old_instance.inspection_status != instance.inspection_status:
            po = instance.purchase_order
            
            if instance.inspection_status == 'ACCEPTED':
                po.status = 'DELIVERED'
                po.request.status = 'COMPLETED'
                po.request.save()
            elif instance.inspection_status == 'REJECTED':
                po.status = 'PENDING'
                po.request.status = 'IN_PROGRESS'
                po.request.save()
            
            po.save()
