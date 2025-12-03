import os
import sys

# Add the project directory to the sys.path
path = os.environ.get('PROJECT_PATH', '/home/<tu_usuario>/almacenes/stock')
if path not in sys.path:
    sys.path.append(path)

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockapp.settings_production')

# Import Django
import django
django.setup()

# Import the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()