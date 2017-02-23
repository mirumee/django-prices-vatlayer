import os

import dj_database_url

SQLITE_DB_URL = 'sqlite:///dev.sqlite'
DATABASES = {
    'default': dj_database_url.config(default=SQLITE_DB_URL, conn_max_age=600)}

SECRET_KEY = 'irrelevant'
INSTALLED_APPS = [
    'django_prices_vatlayer',
]


VATLAYER_ACCESS_KEY = os.environ.get('VATLAYER_ACCESS_KEY', '')
