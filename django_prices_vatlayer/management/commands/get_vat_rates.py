from django.core.management.base import BaseCommand, CommandParser

from ... import utils


class Command(BaseCommand):
    help = 'Get current vat rates in european country and saves to database'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--access_key",
            type=str,
            default=None,
            help=(
               "Provide access_key, required by Vatlayer API. If missing, it will try "
               "to use access_key defined in settings file"
            )
        )

    def handle(self, *args, **options):
        access_key = options.get("access_key") or utils.get_access_key_from_settings()
        utils.fetch_rates(access_key=access_key)
