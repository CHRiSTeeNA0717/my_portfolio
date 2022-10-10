from tl_calculator_bot.settings.common import *
from django.core.management.utils import get_random_secret_key

SECRET_KEY = get_random_secret_key()

DEBUG = True

ALLOWED_HOST = ["127.0.0.1", "localhost"]

STATIC_URL = "/static/"
STATIC_ROOT = "/var/www/static/"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': "dev_db",
        'USER': "dev_user",
        'PASSWORD': "dev_password",
    }
}