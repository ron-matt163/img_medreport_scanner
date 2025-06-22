"""
OCR Engines Module

This module provides a clean interface for OCR operations using different engines.
"""

import logging
from typing import Tuple, Any
from .factory import OCREngineFactory


def initialize_paddle_ocr():
    """Initialize PaddleOCR engine (for backward compatibility)"""
    try:
        OCREngineFactory.get_engine("PaddleOCR")
        logging.info("PaddleOCR initialized via factory")
    except Exception as e:
        logging.error("Failed to initialize PaddleOCR: %s", str(e))


def get_paddle_ocr():
    """Get PaddleOCR engine instance (for backward compatibility)"""
    return OCREngineFactory.get_engine("PaddleOCR")


def is_paddle_ocr_ready():
    """Check if PaddleOCR is ready (for backward compatibility)"""
    engine = OCREngineFactory.get_engine("PaddleOCR")
    return engine.is_ready()


def perform_ocr(img: Any, model_name: str) -> Tuple[str, float]:
    """
    Perform OCR on an image using the specified engine.

    Args:
        img: Image to process (PIL Image or numpy array)
        model_name: Name of the OCR engine ('Tesseract' or 'PaddleOCR')

    Returns:
        Tuple of (extracted_text, average_confidence)

    Raises:
        ValueError: If unknown engine is specified
        RuntimeError: If engine is not ready
    """
    try:
        engine = OCREngineFactory.get_engine(model_name)
        return engine.extract_text(img)
    except Exception as e:
        logging.error("OCR processing failed: %s", str(e))
        raise


def get_available_engines():
    """Get list of available OCR engines"""
    return OCREngineFactory.get_available_engines()


def initialize_all_engines():
    """Initialize all supported OCR engines"""
    OCREngineFactory.initialize_all_engines()
