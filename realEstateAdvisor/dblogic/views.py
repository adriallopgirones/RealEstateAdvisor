from django.http import HttpResponse
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "realEstateAdvisor.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")