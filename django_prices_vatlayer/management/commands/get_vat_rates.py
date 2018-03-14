from django.core.management.base import BaseCommand

from ...utils import (
    create_objects_from_json, fetch_rate_types, fetch_vat_rates,
    save_vat_rate_types)


class Command(BaseCommand):
    help = 'Get current vat rates in european country and saves to database'

    def handle(self, *args, **options):
        json_response_rates = fetch_vat_rates()
        create_objects_from_json(json_response_rates)

        json_response_types = fetch_rate_types()
        save_vat_rate_types(json_response_types)
