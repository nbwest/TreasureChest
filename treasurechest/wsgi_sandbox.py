"""
WSGI config for treasurechest project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""
import os
import time
import traceback
import signal
import sys
from django.core.wsgi import get_wsgi_application

sys.path.append('/usr/local/lib/python2.7/site-packages')

sys.path.append('/var/www/TreasureChest_sandbox')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "treasurechest.settings_sandbox")

try:
    application = get_wsgi_application()
except Exception:
    # Error loading applications
    if 'mod_wsgi' in sys.modules:
        traceback.print_exc()
        os.kill(os.getpid(), signal.SIGINT)
        time.sleep(2.5)