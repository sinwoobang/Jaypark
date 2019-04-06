from django.core.management.base import BaseCommand

from accounts.utils import sync_db_users_to_graph


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        sync_db_users_to_graph()
