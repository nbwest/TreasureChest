"""
Django settings for treasurechest project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG=False
SANDBOX=True
DEVELOPMENT=True



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



