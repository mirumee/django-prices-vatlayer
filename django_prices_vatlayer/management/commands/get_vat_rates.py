from django.core.management.base import BaseCommand

from ...utils import get_european_vat_rates, create_objects_from_json


class Command(BaseCommand):
    help = 'Get current vat rates in european country and saves to database'

    def handle(self, *args, **options):
        json_response = get_european_vat_rates()
        create_objects_from_json(json_response)
