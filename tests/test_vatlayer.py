import pytest

import django
from django.core.exceptions import ImproperlyConfigured


django.setup()


def test_validate_data(json_error, json_success):
    from django_prices_vatlayer.utils import validate_data
    with pytest.raises(ImproperlyConfigured):
        validate_data(json_error)

    assert validate_data(json_success) is None


@pytest.mark.django_db
def test_create_objects_from_json(json_error, json_success):
    from django_prices_vatlayer.utils import create_objects_from_json
    from django_prices_vatlayer.models import Vat

    vat_counts = Vat.objects.count()

    with pytest.raises(ImproperlyConfigured):
        create_objects_from_json(json_error)
    assert vat_counts == Vat.objects.count()

    create_objects_from_json(json_success)
    assert vat_counts + 1 == Vat.objects.count()
