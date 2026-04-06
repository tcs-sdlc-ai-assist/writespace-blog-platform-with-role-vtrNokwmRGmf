import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writespace.settings')

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

application = get_wsgi_application()
app = application

from django.core.management import call_command

try:
    call_command('collectstatic', '--noinput', verbosity=0)
except Exception:
    pass

try:
    call_command('migrate', '--noinput', verbosity=0)
except Exception:
    pass

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'changeme123')
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            password=password,
        )
except Exception:
    pass