from django.apps import AppConfig
from ocr.engines.ocr_engines import initialize_all_engines


class OcrConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ocr"

    def ready(self):
        """Initialize all OCR engines during Django startup"""
        initialize_all_engines()
