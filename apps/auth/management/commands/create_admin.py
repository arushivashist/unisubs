import json
import logging
from optparse import make_option

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Create/Update a user to an admin'

    option_list = BaseCommand.option_list + (
        make_option('--username', action='store', dest='username',
                    default=None, help='Username to be an admin'),
        make_option('--password', action='store', dest='new_password',
                    default=None, help='A new passowrd to be changed - optional'
                    ''),
    )

    def create_admin(self, username, new_password=None):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User(username=username, email="local@amara.org")
        user.is_active = user.is_staff = user.is_superuser = True
        if new_password:
            user.set_password(new_password)
        user.save()

    def handle(self, *langs, **kwargs):
        if kwargs.get('username', None) is not None:
            self.create_admin(kwargs.get("username"), kwargs.get("new_password", None))
