# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
# Uncomment when running in Docker environment
# from .celery import app as celery_app

# __all__ = ('celery_app',)

# Initialize OCR engines during Django startup (only for web service)
import os
import logging

if os.environ.get("DJANGO_SETTINGS_MODULE") and not os.environ.get(
    "CELERY_WORKER_RUNNING"
):
    try:
        from ocr.engines.factory import OCREngineFactory

        # Initialize PaddleOCR during service startup
        OCREngineFactory.get_engine("PaddleOCR")
        logging.info("OCR engines initialized via factory")
    except ImportError as e:
        import logging

        logging.warning("Failed to import OCR engines: %s", str(e))
