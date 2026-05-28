import os

from django.core.asgi import get_asgi_application

os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'

application = get_asgi_application()
