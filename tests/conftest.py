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
    data = {'success': True}
    return data
