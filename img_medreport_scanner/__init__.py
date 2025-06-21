# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
# Uncomment when running in Docker environment
# from .celery import app as celery_app

# __all__ = ('celery_app',)

# Initialize OCR engines during Django startup
try:
    from ocr.engines import ocr_engines
    # Initialize PaddleOCR during service startup
    ocr_engines.initialize_paddle_ocr()
except ImportError as e:
    import logging
    logging.warning("Failed to import OCR engines: %s", str(e))
