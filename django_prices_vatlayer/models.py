from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.translation import pgettext_lazy


class Vat(models.Model):
    country_code = models.CharField(
        pgettext_lazy('Vat field', 'country code'), max_length=2)
    data = JSONField(pgettext_lazy('Vat field', 'data'))
