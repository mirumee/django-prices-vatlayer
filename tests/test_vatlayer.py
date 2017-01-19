import pytest

import django
from django.core.exceptions import ImproperlyConfigured


django.setup()


def test_validate_data(json_error, json_success):
    from django_prices_vatlayer.utils import validate_data
    with pytest.raises(ImproperlyConfigured):
        validate_data(json_error)

    assert validate_data(json_success) is None
