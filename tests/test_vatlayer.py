import pytest
from mock import Mock

import django
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.core.management import call_command


django.setup()


def test_validate_data(json_error, json_success):
    from django_prices_vatlayer.utils import validate_data
    with pytest.raises(ImproperlyConfigured):
        validate_data(json_error)

    assert validate_data(json_success) is None


@pytest.mark.django_db
def test_create_objects_from_json(json_error, json_success):
    from django_prices_vatlayer.utils import create_objects_from_json
    from django_prices_vatlayer.models import Vat

    vat_counts = Vat.objects.count()

    with pytest.raises(ImproperlyConfigured):
        create_objects_from_json(json_error)
    assert vat_counts == Vat.objects.count()

    create_objects_from_json(json_success)
    assert vat_counts + 1 == Vat.objects.count()


def test_get_tax_for_country(vat_country):
    from django_prices_vatlayer.utils import get_tax_for_country

    with pytest.raises(ObjectDoesNotExist):
        get_tax_for_country('XX', 'rate name')

    standard_rate = get_tax_for_country(vat_country.country_code, 'medicine')
    assert standard_rate == 20

    reduced_rate = get_tax_for_country(vat_country.country_code, 'books')
    assert reduced_rate == 10


@pytest.mark.django_db
def test_get_vat_rates_command(monkeypatch, json_success, json_error):
    from django_prices_vatlayer import utils
    from django_prices_vatlayer.models import Vat
    monkeypatch.setattr(utils, 'get_european_vat_rates',
                        lambda: json_success)

    count = Vat.objects.count()
    call_command('get_vat_rates')
    assert count + 1 == Vat.objects.count()
