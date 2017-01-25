from jsonfield import JSONField

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import pgettext_lazy


@python_2_unicode_compatible
class VAT(models.Model):
    country_code = models.CharField(
        pgettext_lazy('Vat field', 'country code'), max_length=2)
    data = JSONField(pgettext_lazy('Vat field', 'data'))

    def __str__(self):
        return self.country_code


class RateTypes(models.Model):
    types = JSONField(pgettext_lazy('Vat field', 'types'))
