from tl_calculator_bot.settings.common import *

DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']

#ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split(",")
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ['DATABASE_NAME'],
        'USER': os.environ['DATABASE_USER'],
        'PASSWORD': os.environ['DATABASE_PASSWORD'],
        'HOST': os.environ['DATABASE_HOST'],
    }
}

#STATICFILES_DIRS = [
#    BASE_DIR / "calculator_app/static",
#    '/var/www/static/',
#]

STATIC_URL = "/static/"
STATIC_ROOT = "/var/www/static/"
