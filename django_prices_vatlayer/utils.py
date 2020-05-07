from decimal import Decimal

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from prices import flat_tax

from .models import VAT, RateTypes, DEFAULT_TYPES_INSTANCE_ID

USE_HTTPS = getattr(settings, 'VATLAYER_USE_HTTPS', False)

PROTOCOL = 'https://' if USE_HTTPS else 'http://'
DEFAULT_URL = PROTOCOL + 'apilayer.net/api/'

VATLAYER_API = getattr(settings, 'VATLAYER_API', DEFAULT_URL)

RATES_URL = 'rate_list'
TYPES_URL = 'types'

CACHE_KEY = getattr(
    settings, 'VATLAYER_CACHE_KEY', 'vatlayer_country_vat_rates')
CACHE_TIME = getattr(settings, 'VATLAYER_CACHE_TTL', 60 * 60)


def validate_data(json_data):
    if not json_data['success']:
        info = json_data['error']['info']
        raise ImproperlyConfigured(info)


def get_access_key_from_settings():
    try:
        key = settings.VATLAYER_ACCESS_KEY
    except AttributeError:
        return None
    return key


def fetch_from_api(url, access_key=None):
    access_key = access_key or get_access_key_from_settings()
    if not access_key:
        raise ImproperlyConfigured(
            "Missing vatlayer acces_key. Provide settings.VATLAYER_ACCESS_KEY or "
            "pass access_key in params argument"
        )
    url = VATLAYER_API + url
    response = requests.get(url, params={'access_key': access_key})
    return response.json()


def fetch_rate_types(access_key=None):
    return fetch_from_api(TYPES_URL, access_key)


def fetch_vat_rates(access_key=None):
    return fetch_from_api(RATES_URL, access_key)


def save_vat_rate_types(json_data):
    validate_data(json_data)

    types = json_data['types']
    RateTypes.objects.update_or_create(
        id=DEFAULT_TYPES_INSTANCE_ID, defaults={'types': types})


def create_objects_from_json(json_data):
    validate_data(json_data)

    # Handle proper response
    rates = json_data['rates']
    for country_code, data in rates.items():
        VAT.objects.update_or_create(
            country_code=country_code, defaults={'data': data})
        country_cache_key = CACHE_KEY + country_code
        cache.set(country_cache_key, data, CACHE_TIME)


def get_tax_rates_for_country(country_code, force_refresh=False):
    country_cache_key = CACHE_KEY + country_code
    tax_rates = cache.get(country_cache_key)
    if not tax_rates or force_refresh:
        try:
            country_vat = VAT.objects.get(country_code=country_code)
            tax_rates = country_vat.data
            cache.set(country_cache_key, tax_rates, CACHE_TIME)
        except ObjectDoesNotExist:
            tax_rates = None
    return tax_rates


def get_tax_rate(tax_rates, rate_name=None):
    if tax_rates is None:
        return None

    try:
        reduced_rates = tax_rates['reduced_rates']
        standard_rate = tax_rates['standard_rate']
    except (KeyError):
        return None

    rate = standard_rate
    if rate_name and reduced_rates and rate_name in reduced_rates:
        rate = reduced_rates[rate_name]

    return rate


def get_tax_for_rate(tax_rates, rate_name=None):
    rate = get_tax_rate(tax_rates, rate_name)
    if rate is None:
        return None

    final_tax_rate = Decimal(rate / 100)

    def tax(base, keep_gross=False):
        return flat_tax(base, final_tax_rate, keep_gross=keep_gross)

    return tax


def get_tax_rate_types():
    rate_types = RateTypes.objects.singleton()
    return rate_types.types if rate_types else []


def fetch_rates(access_key=None):
    json_response_rates = fetch_vat_rates(access_key=access_key)
    create_objects_from_json(json_response_rates)

    json_response_types = fetch_rate_types(access_key=access_key)
    save_vat_rate_types(json_response_types)
