import pytest
from django.core.management import call_command

from django_prices_vatlayer.models import VAT, RateTypes


@pytest.mark.django_db
@pytest.mark.vcr
def test_get_vat_rates_command(settings):
    settings.VATLAYER_ACCESS_KEY = "DUMMY"
    call_command("get_vat_rates")
    assert VAT.objects.exists()
    assert RateTypes.objects.exists()


@pytest.mark.django_db
@pytest.mark.vcr
def test_get_vat_rates_command_access_key_as_a_command_argument():
    call_command("get_vat_rates", access_key="DUMMY")
    assert VAT.objects.exists()
    assert RateTypes.objects.exists()
