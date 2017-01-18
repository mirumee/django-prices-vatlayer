import requests

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import six

from .models import Vat


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


def get_european_vat_rates():
    response = requests.get(RATINGS_URL, params={'access_key': ACCESS_KEY})
    return response.json()


def get_european_vat_types():
    response = requests.get(TYPES_URL, params={'access_key': ACCESS_KEY})
    json_data = response.json()
    validate_data(json_data)
    return json_data['types']


def create_objects_from_json(json_data):
    validate_data(json_data)

    # Handle proper response
    rates = json_data['rates']
    for code, value in six.iteritems(rates):
        Vat.objects.update_or_create(
             country_code=code, defaults={'data': value})
