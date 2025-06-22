"""
URL configuration for img_medreport_scanner project.
"""
from django.urls import path, include

urlpatterns = [path("", include("ocr.urls"))]
