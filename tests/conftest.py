import pytest
import os


def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')


@pytest.fixture
def json_error():
    data = {
        'success': False,
        'error': {'info': 'Invalid json'}
    }
    return data


@pytest.fixture
def json_success():
    data = {'success': True, 'rates': {
        "AT": {"country_name": "Austria", "standard_rate": 20,
               "reduced_rates": {"foodstuffs": 10, "books": 10}}}}
    return data


@pytest.fixture
def vat_country(db):
    from django_prices_vatlayer.models import Vat
    data = {"country_name": "Austria", "standard_rate": 20,
            "reduced_rates": {"foodstuffs": 10, "books": 10}}
    return Vat.objects.create(country_code='AT', data=data)
