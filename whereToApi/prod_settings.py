from whereToApi.settings import *

DEBUG = True

DATABASES = {
  'default': {
    'ENGINE': 'django.contrib.gis.db.backends.postgis',
    'NAME': 'whereTo',
    'HOST': 'whereto.cwcxg0riymqz.eu-central-1.rds.amazonaws.com',
    'PORT': '5432',
    'USER': 'whereTo',
    'PASSWORD': 'msm16531'
  }
}
