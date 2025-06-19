"""
URL configuration for img_medreport_scanner project.
"""
from django.contrib import admin
from django.urls import path
from img_medreport_scanner.views import OCRView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/ocr/", OCRView.as_view(), name="ocr"),
]
