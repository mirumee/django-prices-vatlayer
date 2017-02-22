# django-prices-vatlayer
[Vatlayer API](https://vatlayer.com/) support for django-prices

```python
from prices import Price
from django_prices_vatlayer.utils import get_tax_for_country

tax_for_country = get_tax_for_country('SK', 'books')
price_with_vat = tax_for_country.apply(Price(10, currency='USD'))
print(price_with_vat)
# Price(net='10', gross='11', currency='USD')
print(price_with_vat.history)
# (Price('10', currency='USD') | LinearTax(SK, rate_name=books, vat_rate=10))
```

Installation
==============
First install the package:
```
pip install django-prices-vatlayer
```
Then add `'django_prices_vatlayer'` to your `INSTALLED_APPS`.

Set following settings in your project's settings:

 * `VATLAYER_ACCESS_KEY`
 *  To safeguard against DNS poisoning and man-in-the-middle attacks we recommend that `VATLAYER_API` is set to use the HTTPS endpoint which is the default when running in production mode. The secure endpoint is only available with paid plans.



Update vat rates
=======================
Fetch current vat rates from API with `./manage.py get_vat_rates`

Schedule this task in cron job or in celery, to be always up to date with exchange rates
