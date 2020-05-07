from unittest.mock import Mock

import pytest
from django.core.exceptions import ImproperlyConfigured
from django_prices_vatlayer import utils
from django_prices_vatlayer.models import VAT, RateTypes
from prices import Money, TaxedMoney


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


@pytest.mark.vcr
def test_fetch_vat_rates_api_key_passed_in_params():
    rates = utils.fetch_vat_rates(access_key="DUMMY")
    assert rates['success']
    assert 'rates' in rates


@pytest.mark.vcr
def test_fetch_vat_rates_api_key_from_settings(settings):
    settings.VATLAYER_ACCESS_KEY = "DUMMY"
    rates = utils.fetch_vat_rates()
    assert rates['success']
    assert 'rates' in rates


@pytest.mark.vcr
def test_fetch_rate_types_api_key_from_settings(settings):
    settings.VATLAYER_ACCESS_KEY = "DUMMY"
    rate_types = utils.fetch_rate_types()
    assert rate_types['success']
    assert 'types' in rate_types


@pytest.mark.vcr
def test_fetch_rate_types_api_key_passed_in_params():
    rates = utils.fetch_rate_types(access_key="DUMMY")
    assert rates['success']
    assert 'types' in rates


@pytest.mark.django_db
@pytest.mark.vcr
def test_fetch_rates_api_key_in_params():
    utils.fetch_rates(access_key="DUMMY")
    assert VAT.objects.exists()
    assert RateTypes.objects.exists()


def test_fetch_from_api_raises_exception_when_api_key_is_missing():
    with pytest.raises(ImproperlyConfigured):
        utils.fetch_from_api(utils.TYPES_URL)


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


@pytest.mark.django_db
def test_get_tax_rate_types(rate_type):
    rate_types = utils.get_tax_rate_types()
    assert rate_types == rate_type.types


@pytest.mark.django_db
def test_get_tax_rate_types_no_rate_types():
    rate_types = utils.get_tax_rate_types()
    assert rate_types == []


def test_get_tax_rates_for_country(vat_country):
    country_code = vat_country.country_code
    tax_rates = utils.get_tax_rates_for_country(country_code)
    assert tax_rates['country_name'] == 'Austria'
    assert tax_rates['standard_rate'] == 20
    assert tax_rates['reduced_rates'] == {'books': 10, 'foodstuffs': 10}


def test_get_tax_rates_for_country_without_reduced_rates(
        vat_without_reduced_rates):
    country_code = vat_without_reduced_rates.country_code
    tax_rates = utils.get_tax_rates_for_country(country_code)
    assert tax_rates['country_name'] == 'Austria'
    assert tax_rates['standard_rate'] == 20
    assert tax_rates['reduced_rates'] is None


@pytest.mark.django_db
def test_get_tax_rates_for_country_invalid_code():
    tax_rates = utils.get_tax_rates_for_country('XX')
    assert tax_rates is None


def test_get_tax_rate_standard_rate(vat_country):
    tax_rates = vat_country.data
    standard_rate = utils.get_tax_rate(tax_rates)
    assert standard_rate == tax_rates['standard_rate']


def test_get_tax_rate_fallback_to_standard_rate(vat_without_reduced_rates):
    tax_rates = vat_without_reduced_rates.data
    hotels_rate = utils.get_tax_rate(tax_rates, 'hotels')
    assert hotels_rate == tax_rates['standard_rate']


def test_get_tax_rate_reduced_rate(vat_country):
    tax_rates = vat_country.data
    books_rate = utils.get_tax_rate(tax_rates, 'books')
    assert books_rate == tax_rates['reduced_rates']['books']


def test_get_tax_for_rate_standard_rate(vat_country):
    tax_rates = vat_country.data
    standard_tax = utils.get_tax_for_rate(tax_rates)

    assert standard_tax(Money(100, 'USD')) == TaxedMoney(
        net=Money(100, 'USD'), gross=Money(120, 'USD'))
    assert standard_tax(Money(100, 'USD'), keep_gross=True) == TaxedMoney(
        net=Money('83.33', 'USD'), gross=Money(100, 'USD'))

    taxed_money = TaxedMoney(net=Money(100, 'USD'), gross=Money(100, 'USD'))
    assert standard_tax(taxed_money) == TaxedMoney(
        net=Money(100, 'USD'), gross=Money(120, 'USD'))
    assert standard_tax(taxed_money, keep_gross=True) == TaxedMoney(
        net=Money('83.33', 'USD'), gross=Money(100, 'USD'))


def test_get_tax_for_rate_fallback_to_standard_rate(vat_country):
    tax_rates = vat_country.data
    hotels_tax = utils.get_tax_for_rate(tax_rates, 'hotels')

    assert hotels_tax(Money(100, 'USD')) == TaxedMoney(
        net=Money(100, 'USD'), gross=Money(120, 'USD'))
    assert hotels_tax(Money(100, 'USD'), keep_gross=True) == TaxedMoney(
        net=Money('83.33', 'USD'), gross=Money(100, 'USD'))

    taxed_money = TaxedMoney(net=Money(100, 'USD'), gross=Money(100, 'USD'))
    assert hotels_tax(taxed_money) == TaxedMoney(
        net=Money(100, 'USD'), gross=Money(120, 'USD'))
    assert hotels_tax(taxed_money, keep_gross=True) == TaxedMoney(
        net=Money('83.33', 'USD'), gross=Money(100, 'USD'))


def test_get_tax_for_rate_reduced_rate(vat_country):
    tax_rates = vat_country.data
    books_tax = utils.get_tax_for_rate(tax_rates, 'books')

    assert books_tax(Money(100, 'USD')) == TaxedMoney(
        net=Money(100, 'USD'), gross=Money(110, 'USD'))
    assert books_tax(Money(100, 'USD'), keep_gross=True) == TaxedMoney(
        net=Money('90.91', 'USD'), gross=Money(100, 'USD'))

    taxed_money = TaxedMoney(net=Money(100, 'USD'), gross=Money(100, 'USD'))
    assert books_tax(taxed_money) == TaxedMoney(
        net=Money(100, 'USD'), gross=Money(110, 'USD'))
    assert books_tax(taxed_money, keep_gross=True) == TaxedMoney(
        net=Money('90.91', 'USD'), gross=Money(100, 'USD'))
