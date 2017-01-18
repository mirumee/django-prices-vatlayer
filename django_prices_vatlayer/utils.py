import json

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .models import Vat


try:
    ACCESS_KEY = settings.VATLAYER_ACCESS_KEY
except AttributeError:
    raise ImproperlyConfigured('VATLAYER_ACCESS_KEY is required')


def get_european_vat_rates():
    pass