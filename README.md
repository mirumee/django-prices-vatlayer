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


Forcing secure API connection in production
-------------------------------------------

Because HTTPS is unavailable in the free vatlayer plan, `django-prices-vatlayer` uses the unsafe HTTP connection by default.

If you are using a paid plan, you can force the secure HTTP on your site by adding following line to your `settings.py`:

```python
VATLAYER_USE_HTTPS = True
```

Remember that not using HTTPS may expose you to DNS poisoning and man-in-the-middle attacks; we recommend enabling `VATLAYER_USE_HTTPS` in production sites.


Updating VAT rates
==================

To get current VAT rates from the API run the `get_vat_rates` management command.

You may also set cron job for running this task daily to always be up to date with current tax rates.
