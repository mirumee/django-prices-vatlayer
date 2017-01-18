import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'}}

SECRET_KEY = 'irrelevant'
INSTALLED_APPS = [
    'django_prices_vatlayer'
]


VATLAYER_ACCESS_KEY = os.environ.get('VATLAYER_ACCESS_KEY', '')
