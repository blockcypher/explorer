"""
WSGI config for blockexplorer project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

from raven.contrib.django.raven_compat.middleware.wsgi import Sentry
# http://raven.readthedocs.org/en/latest/config/django.html#wsgi-middleware

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blockexplorer.settings")

from dj_static import Cling

from django.core.wsgi import get_wsgi_application
application = Sentry(Cling(get_wsgi_application()))
