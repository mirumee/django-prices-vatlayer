import requests

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .models import Vat


try:
    ACCESS_KEY = settings.VATLAYER_ACCESS_KEY
except AttributeError:
    raise ImproperlyConfigured('VATLAYER_ACCESS_KEY is required')

RATINGS_URL = 'http://apilayer.net/api/rate_list'


def get_european_vat_rates():
    response = requests.get(RATINGS_URL, params={'access_key': ACCESS_KEY})
    return response.json()
