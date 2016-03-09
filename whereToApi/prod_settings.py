from .settings import *

DEBUG = False

DATABASES = {
  'default': {
    'ENGINE': 'django.contrib.gis.db.backends.postgis',
    'NAME': 'whereTo',
    'HOST': 'localhost',
    'PORT': '5432',
    'USER': 'whereTo',
    'PASSWORD': 'msm16531'
  }
}
