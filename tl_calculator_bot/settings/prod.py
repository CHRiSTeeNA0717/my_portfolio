from tl_calculator_bot.settings.common import *
from tl_calculator_bot.tl_calculator_bot.settings.dev import SECRET_KEY

DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['0.0.0.0', 'localhost']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ['DATABASE_NAME'],
        'USER': os.environ['DATABASE_USER'],
        'PASSWORD': os.environ['DATABASE_PASSWORD'],
    }
}

STATICFILES_DIRS = [
    BASE_DIR / "calculator_app/static",
    '/var/www/static/',
]