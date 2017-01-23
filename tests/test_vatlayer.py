import django
django.setup()

from prices import Price, PriceRange
from decimal import Decimal
import pytest

from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command

from django_prices_vatlayer import utils
from django_prices_vatlayer.european_vat import EuropeanVAT, get_price_with_vat
from django_prices_vatlayer.models import EuropeanVatRate


@pytest.fixture
def vat_country(db, json_success):
    data = json_success['rates']['AT']
    return EuropeanVatRate.objects.create(country_code='AT', data=data)


@pytest.fixture
def vat_without_rates(db):
    return EuropeanVatRate.objects.create(country_code='AU', data={})


@pytest.fixture
def get_european_vat_rates_success(monkeypatch, json_success):
    monkeypatch.setattr(utils, 'get_european_vat_rates',
                        lambda: json_success)


@pytest.fixture
def get_european_vat_rates_error(monkeypatch, json_error):
    monkeypatch.setattr(utils, 'get_european_vat_rates',
                        lambda: json_error)


def test_validate_data_invalid(json_error):
    with pytest.raises(ImproperlyConfigured):
        utils.validate_data(json_error)


def test_validate_data_valid(json_success):
    assert utils.validate_data(json_success) is None


@pytest.mark.django_db
def test_create_objects_from_json(json_error, json_success):

    vat_counts = EuropeanVatRate.objects.count()

    with pytest.raises(ImproperlyConfigured):
        utils.create_objects_from_json(json_error)

    utils.create_objects_from_json(json_success)
    assert vat_counts + 1 == EuropeanVatRate.objects.count()


@pytest.mark.parametrize('rate_name,expected',
                         [('medicine', Decimal(20)), ('books', Decimal(10)),
                          (None, Decimal(20))])
def test_get_tax_for_country(vat_country, rate_name, expected):
    country_code = vat_country.country_code
    rate = utils.get_tax_for_country(country_code, rate_name)
    assert rate == expected


@pytest.mark.django_db
def test_get_tax_for_country_error():
    rate = utils.get_tax_for_country('XX', 'rate name')
    assert rate is None


@pytest.mark.django_db
def test_get_vat_rates_command(monkeypatch, get_european_vat_rates_success):

    call_command('get_vat_rates')
    assert 1 == EuropeanVatRate.objects.count()


@pytest.mark.django_db
def test_get_vat_rates_command(monkeypatch, get_european_vat_rates_error):

    with pytest.raises(ImproperlyConfigured):
        call_command('get_vat_rates')


@pytest.mark.django_db
@pytest.mark.parametrize('european_vat',
                         [EuropeanVAT('TT', 'books'),
                          EuropeanVAT('AU', 'books')])
def test_european_vat_calculate_tax(vat_without_rates, european_vat):
    price = Price(net=100)

    tax_value = european_vat.calculate_tax(price)
    assert tax_value == 0


@pytest.mark.django_db
def test_european_vat_calculate_tax_valid(vat_country):
    vat_books = EuropeanVAT('AT', 'books')
    price = Price(net=100)
    tax_value = vat_books.calculate_tax(price)
    assert tax_value == 10


@pytest.mark.django_db
@pytest.mark.parametrize('european_vat, gross',
                         [(EuropeanVAT('AT', 'books'), 121),
                          (EuropeanVAT('TT', 'books'), 110),
                          (EuropeanVAT('AU', 'books'), 110),
                          (EuropeanVAT('AT'), 132)])
def test_european_vat_apply(vat_country, vat_without_rates,
                            gross, european_vat):
    price = Price(net=100, gross=110)

    tax_value = european_vat.apply(price)
    assert tax_value.gross == gross


@pytest.mark.django_db
@pytest.mark.parametrize(
    'price, expected',
    [(Price(net=100, gross=110), Price(net=100, gross=121)),
     (PriceRange(Price(net=100, gross=110), Price(net=200, gross=220)),
      PriceRange(Price(net=100, gross=121), Price(net=200, gross=242)))])
def test_get_price_with_vat(vat_country, price, expected):
    price_with_vat = get_price_with_vat('AT', price, 'books')
    assert price_with_vat == expected


@pytest.mark.django_db
def test_get_price_with_vat_without_rate_name(vat_country):
    price = Price(net=100, gross=110)
    price_with_vat = get_price_with_vat('AT', price)
    assert price_with_vat == Price(net=100, gross=132)
