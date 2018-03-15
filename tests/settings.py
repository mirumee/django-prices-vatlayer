import os

SECRET_KEY = 'irrelevant'

INSTALLED_APPS = ['django_prices_vatlayer']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'database.sqlite'}}

VATLAYER_ACCESS_KEY = os.environ.get('VATLAYER_ACCESS_KEY', '')
