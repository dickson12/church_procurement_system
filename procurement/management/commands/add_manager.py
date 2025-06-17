from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from ._utils import add_user_to_group

class Command(BaseCommand):
    help = 'Add a user to the Management group'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to add to Management group')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        add_user_to_group(username, 'Management')
