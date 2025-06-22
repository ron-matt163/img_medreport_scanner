from celery import Celery
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "img_medreport_scanner.settings")

app = Celery("img_medreport_scanner")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
