django-prices-vatlayer: [Vatlayer API](https://vatlayer.com/) support for `prices`
=======================================================

[![Build Status](https://secure.travis-ci.org/mirumee/django-prices-vatlayer.png)](https://travis-ci.org/mirumee/django-prices-vatlayer) [![codecov.io](https://img.shields.io/codecov/c/github/mirumee/django-prices-vatlayer/master.svg)](http://codecov.io/github/mirumee/django-prices-vatlayer?branch=master)

```python
from prices import Money, TaxedMoney
from django_prices_vatlayer.utils import (
    get_tax_for_rate, get_tax_rates_for_country)

de_tax_rates = get_tax_rates_for_country('DE')
books_tax = get_tax_for_rate(de_tax_rates, 'books')

price_with_vat = books_tax(Money(10, 'EUR'))
print(price_with_vat)
# TaxedMoney(net=Money('10', 'EUR'), gross=Money('11', 'EUR'))

price_with_vat = books_tax(
    TaxedMoney(net=Money(10, 'EUR'), gross=Money(10, 'EUR')))
print(price_with_vat)
# TaxedMoney(net=Money('10', 'EUR'), gross=Money('11', 'EUR'))
```


Installation
============

The package can easily be installed via pip:

```
pip install django-prices-vatlayer
```

After installation, you'll also need to setup your site to use it. To do that, open your `settings.py` and do the following:

1. Add `'django_prices_vatlayer',` to your `INSTALLED_APPS`
2. Add `VATLAYER_ACCESS_KEY = 'YOUR_API_KEY_HERE'` line
3. Replace `YOUR_API_KEY_HERE` with the API key that you have obtained from vatlayer API

Lastly, run `manage.py migrate` to create new tables in your database and `manage.py get_vat_rates` to populate them with initial data.


Forcing non-secure API connection in production
-----------------------------------------------

By default, `django-prices-vatlayer` uses the unsafe HTTP connection during development (`DEBUG = True`) and changes to HTTPS in production, to keep communication with the `vatlayer` API secure.

However as HTTPS unavailable in vatlayer's free plan, you may preffer to force unsafe HTTP on your live site as well. To do so, just add following line to your `settings.py`:

`VATLAYER_API = 'http://apilayer.net/api/'`

Remember that doing so may expose you to DNS poisoning and man-in-the-middle attacks and we recommend that `VATLAYER_API` is set to use the HTTPS.


Updating VAT rates
==================

To get current VAT rates from the API run the `get_vat_rates` management command.

You may also set cron job for running this task daily to always be up to date with current tax rates.
