from prices import LinearTax
import requests

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.utils import six

from .models import VAT

try:
    ACCESS_KEY = settings.VATLAYER_ACCESS_KEY
except AttributeError:
    raise ImproperlyConfigured('VATLAYER_ACCESS_KEY is required')

RATINGS_URL = 'http://apilayer.net/api/rate_list'
TYPES_URL = 'http://apilayer.net/api/types'


def validate_data(json_data):
    if not json_data['success']:
        info = json_data['error']['info']
        raise ImproperlyConfigured(info)


def fetch_from_api(url):
    response = requests.get(url, params={'access_key': ACCESS_KEY})
    return response.json()


def fetch_rates_types():
    return fetch_from_api(TYPES_URL)


def fetch_vat_rates():
    return fetch_from_api(RATINGS_URL)


def create_objects_from_json(json_data):
    validate_data(json_data)

    # Handle proper response
    rates = json_data['rates']
    for code, value in six.iteritems(rates):
        VAT.objects.update_or_create(
             country_code=code, defaults={'data': value})


def get_tax_for_country(country_code, rate_name=None):
    try:
        country_vat = VAT.objects.get(country_code=country_code)
        reduced_rates = country_vat.data['reduced_rates']
        standard_rate = country_vat.data['standard_rate']
    except (KeyError, ObjectDoesNotExist):
        return None

    rate = standard_rate
    if rate_name is not None and rate_name in six.iterkeys(reduced_rates):
        rate = reduced_rates[rate_name]

    tax_name = '%s - %s' % (country_code, rate_name)

    return LinearTax(rate/100, tax_name)
