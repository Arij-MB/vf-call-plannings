from django.core.management.base import BaseCommand
from vf_call_plannings.view import maran_check


class Command(BaseCommand):
    help = 'Checks the Scrapper_maranfleet table and updates the Maran_error_report table'

    def handle(self, *args, **options):
        maran_check()
        self.stdout.write(self.style.SUCCESS('Successfully checked scrapper_maranfleet table'))
