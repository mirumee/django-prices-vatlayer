from __future__ import division
from prices import LinearTax
import pytest

from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command

from django_prices_vatlayer import utils
from django_prices_vatlayer.models import VAT, RateTypes


@pytest.fixture
def vat_country(db, json_success):
    data = json_success['rates']['AT']
    return VAT.objects.create(country_code='AT', data=data)


@pytest.fixture
def vat_without_rates(db):
    return VAT.objects.create(country_code='AU', data={})


@pytest.fixture
def vat_without_reduced_rates(db, json_success_without_reduced_rates):
    data = json_success_without_reduced_rates['rates']['AZ']
    return VAT.objects.create(country_code='AZ', data=data)


@pytest.fixture
def rate_type(db):
    return RateTypes.objects.create(types=['books'])


@pytest.fixture
def fetch_vat_rates_success(monkeypatch, json_success):
    monkeypatch.setattr(utils, 'fetch_vat_rates',
                        lambda: json_success)


@pytest.fixture
def fetch_vat_rates_error(monkeypatch, json_error):
    monkeypatch.setattr(utils, 'fetch_vat_rates',
                        lambda: json_error)


@pytest.fixture
def fetch_rate_types_success(monkeypatch, json_types_success):
    monkeypatch.setattr(utils, 'fetch_rate_types',
                        lambda: json_types_success)


@pytest.fixture
def fetch_rate_types_error(monkeypatch, json_error):
    monkeypatch.setattr(utils, 'fetch_rate_types',
                        lambda: json_error)


def test_validate_data_invalid(json_error):
    with pytest.raises(ImproperlyConfigured):
        utils.validate_data(json_error)


def test_validate_data_valid(json_success):
    assert utils.validate_data(json_success) is None


@pytest.mark.django_db
def test_create_objects_from_json_error(json_error, json_success):

    vat_counts = VAT.objects.count()

    with pytest.raises(ImproperlyConfigured):
        utils.create_objects_from_json(json_error)

    utils.create_objects_from_json(json_success)
    assert vat_counts + 1 == VAT.objects.count()


@pytest.mark.django_db
def test_create_objects_from_json_success(
        json_success, json_success_without_reduced_rates):
    for json_dict in [json_success, json_success_without_reduced_rates]:
        utils.create_objects_from_json(json_dict)
    assert VAT.objects.count() == 2


@pytest.mark.django_db
def test_save_vat_rate_types(json_types_success):
    utils.save_vat_rate_types(json_types_success)
    assert 1 == RateTypes.objects.count()

    utils.save_vat_rate_types(json_types_success)
    assert 1 == RateTypes.objects.count()


@pytest.mark.parametrize('rate_name,expected',
                         [('medicine', LinearTax(20/100, 'AT - medicine')),
                          ('standard', LinearTax(20/100, 'AT - standard')),
                          ('books', LinearTax(10/100, 'AT - books')),
                          (None, LinearTax(20/100, 'AT - None'))])
def test_get_tax_for_country(vat_country, rate_name, expected):
    country_code = vat_country.country_code
    rate = utils.get_tax_for_country(country_code, rate_name)
    assert rate == expected


@pytest.mark.parametrize('rate_name,expected',
                         [('medicine', LinearTax(20/100, 'AZ - medicine')),
                          ('standard', LinearTax(20/100, 'AZ - standard')),
                          (None, LinearTax(20/100, 'AZ - None'))])
def test_get_tax_for_country(vat_without_reduced_rates, rate_name, expected):
    country_code = vat_without_reduced_rates.country_code
    rate = utils.get_tax_for_country(country_code, rate_name)
    assert rate == expected


@pytest.mark.django_db
def test_get_tax_for_country_error():
    rate = utils.get_tax_for_country('XX', 'rate name')
    assert rate is None


@pytest.mark.django_db
def test_get_vat_rates_command(fetch_vat_rates_success,
                               fetch_rate_types_success):

    call_command('get_vat_rates')
    assert 1 == VAT.objects.count()
    assert 1 == RateTypes.objects.count()


@pytest.mark.django_db
def test_get_vat_rates_command(fetch_vat_rates_error, fetch_rate_types_success):

    with pytest.raises(ImproperlyConfigured):
        call_command('get_vat_rates')


@pytest.mark.django_db
def test_get_vat_rates_command(fetch_vat_rates_success,
                               fetch_rate_types_error):

    with pytest.raises(ImproperlyConfigured):
        call_command('get_vat_rates')


@pytest.mark.django_db
def test_singleton(rate_type):
    assert RateTypes.objects.singleton() == rate_type
