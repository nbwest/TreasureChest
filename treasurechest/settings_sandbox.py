"""
Django settings for treasurechest project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

from settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG=True
SANDBOX=True
DEVELOPMENT=True

ALLOWED_HOSTS = ['localhost', '127.0.0.1','67.209.127.188','sandbox.megstoybox.org']

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 6 * 60 * 60#
# Database
DATABASES = {
'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'toybox_sandbox',
        'USER': 'toyboxuser',
        'PASSWORD': 'sspokess',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}



