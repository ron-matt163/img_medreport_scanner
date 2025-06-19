"""
URL configuration for img_medreport_scanner project.
"""
from django.urls import path
from img_medreport_scanner.views import OCRView

urlpatterns = [
    path("ocr/", OCRView.as_view(), name="ocr"),
]
