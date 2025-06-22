from django.urls import path
from ocr.views import OCRView

app_name = "ocr"

urlpatterns = [
    path("ocr/", OCRView.as_view(), name="ocr"),
]
