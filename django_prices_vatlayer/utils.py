from __future__ import division
from prices import LinearTax
import requests

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.utils import six

from .models import VAT, RateTypes, DEFAULT_TYPES_INSTANCE_ID

try:
    ACCESS_KEY = settings.VATLAYER_ACCESS_KEY
except AttributeError:
    raise ImproperlyConfigured('VATLAYER_ACCESS_KEY is required')

PROTOCOL = 'http://' if settings.DEBUG else 'https://'
DEFAULT_URL = PROTOCOL + 'apilayer.net/api/'

VATLAYER_API = getattr(
    settings, 'VATLAYER_API', DEFAULT_URL)

RATINGS_URL = 'rate_list'
TYPES_URL = 'types'


def validate_data(json_data):
    if not json_data['success']:
        info = json_data['error']['info']
        raise ImproperlyConfigured(info)


def fetch_from_api(url):
    url = VATLAYER_API + url
    response = requests.get(url, params={'access_key': ACCESS_KEY})
    return response.json()


def fetch_rate_types():
    return fetch_from_api(TYPES_URL)


def fetch_vat_rates():
    return fetch_from_api(RATINGS_URL)


def save_vat_rate_types(json_data):
    validate_data(json_data)

    types = json_data['types']
    RateTypes.objects.update_or_create(id=DEFAULT_TYPES_INSTANCE_ID,
                                       defaults={'types': types})


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
    if rate_name and reduced_rates and rate_name in six.iterkeys(reduced_rates):
        rate = reduced_rates[rate_name]

    tax_name = '%s - %s' % (country_code, rate_name)

    return LinearTax(rate/100, tax_name)
