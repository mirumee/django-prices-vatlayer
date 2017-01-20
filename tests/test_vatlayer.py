import django
django.setup()

from prices import Price
from decimal import Decimal
import pytest

from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.core.management import call_command

from django_prices_vatlayer import utils
from django_prices_vatlayer.european_vat import EuropeanVAT
from django_prices_vatlayer.models import Vat


@pytest.fixture
def vat_country(db, json_success):
    data = json_success['rates']['AT']
    return Vat.objects.create(country_code='AT', data=data)


@pytest.fixture
def vat_without_rates(db):
    return Vat.objects.create(country_code='AU', data={})


def test_validate_data_invalid(json_error):
    with pytest.raises(ImproperlyConfigured):
        utils.validate_data(json_error)


def test_validate_data_valid(json_success):
    assert utils.validate_data(json_success) is None


@pytest.mark.django_db
def test_create_objects_from_json(json_error, json_success):

    vat_counts = Vat.objects.count()

    with pytest.raises(ImproperlyConfigured):
        utils.create_objects_from_json(json_error)

    utils.create_objects_from_json(json_success)
    assert vat_counts + 1 == Vat.objects.count()


@pytest.mark.parametrize('rate_name,expected',
                         [('medicine', Decimal(20)), ('books', Decimal(10))])
def test_get_tax_for_country(vat_country, rate_name, expected):
    country_code = vat_country.country_code
    rate = utils.get_tax_for_country(country_code, rate_name)
    assert rate == expected


@pytest.mark.django_db
def test_get_tax_for_country_error():
    with pytest.raises(ObjectDoesNotExist):
        utils.get_tax_for_country('XX', 'rate name')


@pytest.mark.django_db
def test_get_vat_rates_command(monkeypatch, json_success):
    monkeypatch.setattr(utils, 'get_european_vat_rates',
                        lambda: json_success)

    call_command('get_vat_rates')
    assert 1 == Vat.objects.count()


@pytest.mark.django_db
@pytest.mark.parametrize('european_vat,error',
                         [(EuropeanVAT('TT', 'books'), ObjectDoesNotExist),
                          (EuropeanVAT('AU', 'books'), KeyError)])
def test_european_vat_calculate_tax(vat_without_rates, european_vat, error):
    price = Price(net=100)

    with pytest.raises(error):
        tax_value = european_vat.calculate_tax(price)


@pytest.mark.django_db
def test_european_vat_calculate_tax_valid(vat_country):
    vat_books = EuropeanVAT('AT', 'books')
    price = Price(net=100)
    tax_value = vat_books.calculate_tax(price)
    assert tax_value == 10


@pytest.mark.django_db
def test_european_vat_apply(vat_country, vat_without_rates):
    vat_books = EuropeanVAT('AT', 'books')
    price = Price(net=100, gross=110)
    tax_value = vat_books.apply(price)
    assert tax_value.gross == 121

    vat_wrong_country = EuropeanVAT('TT', 'books')

    tax_value = vat_wrong_country.apply(price)
    assert tax_value.gross == price.gross

    vat_without_rates = EuropeanVAT('AU', 'books')

    tax_value = vat_without_rates.apply(price)
    assert tax_value == price
