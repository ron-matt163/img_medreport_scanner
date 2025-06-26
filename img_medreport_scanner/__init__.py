# Initialize OCR engines during Django startup (synchronous processing)
import os
import logging

if os.environ.get("DJANGO_SETTINGS_MODULE"):
    try:
        from ocr.engines.factory import OCREngineFactory

        # Initialize all OCR engines during service startup
        OCREngineFactory.initialize_all_engines()
        logging.info("All OCR engines initialized for synchronous processing")
    except ImportError as e:
        logging.warning("Failed to import OCR engines: %s", str(e))
