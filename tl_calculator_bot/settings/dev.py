from tl_calculator_bot.settings.common import *

# this file should only exists on dev environment aka local machine
# this file should be added to .gitignore

DEBUG = True
SECRET_KEY="django-insecure-t1l34ghf%3(=ngmpe6y1#erf(l+^bn0_9x#pj!a1fjgks"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_ROOT = BASE_DIR / 'calculator_app/static'