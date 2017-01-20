import requests
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.utils import six

from .models import EuropeanVatRate

try:
    ACCESS_KEY = settings.VATLAYER_ACCESS_KEY
except AttributeError:
    raise ImproperlyConfigured('VATLAYER_ACCESS_KEY is required')

RATINGS_URL = 'http://apilayer.net/api/rate_list'


def validate_data(json_data):
    if not json_data['success']:
        info = json_data['error']['info']
        raise ImproperlyConfigured(info)


def get_european_vat_rates():
    response = requests.get(RATINGS_URL, params={'access_key': ACCESS_KEY})
    return response.json()


def create_objects_from_json(json_data):

    validate_data(json_data)

    # Handle proper response
    rates = json_data['rates']
    for code, value in six.iteritems(rates):
        EuropeanVatRate.objects.update_or_create(
             country_code=code, defaults={'data': value})


def get_tax_for_country(country_code, rate_name):
    try:
        country_vat = EuropeanVatRate.objects.get(country_code=country_code)
        reduced_rates = country_vat.data['reduced_rates']
        standard_rate = country_vat.data['standard_rate']
    except (KeyError, ObjectDoesNotExist):
        return None

    try:
        rate = reduced_rates[rate_name]
    except KeyError:
        rate = standard_rate
    return Decimal(rate)
