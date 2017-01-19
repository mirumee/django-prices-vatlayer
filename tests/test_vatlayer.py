import pytest
from prices import Price

import django
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.core.management import call_command

from django_prices_vatlayer import utils, EuropeanVAT

django.setup()


def test_validate_data(json_error, json_success):
    with pytest.raises(ImproperlyConfigured):
        utils.validate_data(json_error)

    assert utils.validate_data(json_success) is None


@pytest.mark.django_db
def test_create_objects_from_json(json_error, json_success):
    from django_prices_vatlayer.models import Vat

    vat_counts = Vat.objects.count()

    with pytest.raises(ImproperlyConfigured):
        utils.create_objects_from_json(json_error)
    assert vat_counts == Vat.objects.count()

    utils.create_objects_from_json(json_success)
    assert vat_counts + 1 == Vat.objects.count()


def test_get_tax_for_country(vat_country):
    with pytest.raises(ObjectDoesNotExist):
        utils.get_tax_for_country('XX', 'rate name')

    country_code = vat_country.country_code
    standard_rate = utils.get_tax_for_country(country_code, 'medicine')
    assert standard_rate == 20

    reduced_rate = utils.get_tax_for_country(country_code, 'books')
    assert reduced_rate == 10


@pytest.mark.django_db
def test_get_vat_rates_command(monkeypatch, json_success):
    from django_prices_vatlayer.models import Vat
    monkeypatch.setattr(utils, 'get_european_vat_rates',
                        lambda: json_success)

    count = Vat.objects.count()
    call_command('get_vat_rates')
    assert count + 1 == Vat.objects.count()


@pytest.mark.django_db
def test_european_vat_calculate_tax(vat_country):
    from django_prices_vatlayer.models import Vat
    vat_books = EuropeanVAT('AT', 'books')
    price = Price(net=100)
    tax_value = vat_books.calculate_tax(price)
    assert tax_value == 10

    vat_wrong_country = EuropeanVAT('TT', 'books')

    with pytest.raises(ObjectDoesNotExist):
        tax_value = vat_wrong_country.calculate_tax(price)

    Vat.objects.create(country_code='AU', data={})
    vat_without_rates = EuropeanVAT('AU', 'books')

    with pytest.raises(KeyError):
        tax_value = vat_without_rates.calculate_tax(price)


@pytest.mark.django_db
def test_european_vat_apply(vat_country):
    from django_prices_vatlayer.models import Vat
    vat_books = EuropeanVAT('AT', 'books')
    price = Price(net=100)
    tax_value = vat_books.apply(price)
    assert tax_value.gross == 110

    vat_wrong_country = EuropeanVAT('TT', 'books')

    tax_value = vat_wrong_country.apply(price)
    assert tax_value == price

    Vat.objects.create(country_code='AU', data={})
    vat_without_rates = EuropeanVAT('AU', 'books')

    tax_value = vat_without_rates.apply(price)
    assert tax_value == price