from django.core.management.base import BaseCommand
from vf_call_plannings.view import maran_check


# class Command(BaseCommand):
#     help = 'Checks the Scrapper_maranfleet table and updates the Maran_error_report table'
#
#     def handle(self, *args, **options):
#         maran_check()
#         self.stdout.write(self.style.SUCCESS('Successfully checked scrapper_maranfleet table'))

class Command(BaseCommand):
    help = 'Executes the cron job for view Maran'

    def handle(self, *args, **options):
        maran_vf_logger.info('Cron Job for Maran started')
        # Create an instance of HttpRequest to simulate the POST request
        factory = RequestFactory()
        request = factory.post('/my_view/')

        # Call the view method with the simulated request
        maran_check()

        # Log the response or perform any other necessary actions
        maran_vf_logger.info('Cron Job for Maran finished')