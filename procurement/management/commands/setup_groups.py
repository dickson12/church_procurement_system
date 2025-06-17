from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from procurement.models import PurchaseRequest

class Command(BaseCommand):
    help = 'Create default groups and permissions'

    def handle(self, *args, **kwargs):
        # Create Management group
        management_group, created = Group.objects.get_or_create(name='Management')
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created Management group'))
        else:
            self.stdout.write('Management group already exists')

        # Add permissions for PurchaseRequest to Management group
        content_type = ContentType.objects.get_for_model(PurchaseRequest)
        permissions = Permission.objects.filter(content_type=content_type)
        for permission in permissions:
            management_group.permissions.add(permission)

        # Create Staff group
        staff_group, created = Group.objects.get_or_create(name='Staff')
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created Staff group'))
        else:
            self.stdout.write('Staff group already exists')

        # Add superuser to Management group if they exist
        try:
            admin = User.objects.get(username='admin', is_superuser=True)
            admin.groups.add(management_group)
            self.stdout.write(self.style.SUCCESS(f'Added admin user to Management group'))
        except User.DoesNotExist:
            self.stdout.write('Superuser not found')
