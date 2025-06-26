import pytesseract
import logging
from typing import Tuple, Any
from PIL import Image
from django.conf import settings
from .base import BaseOCREngine


class TesseractEngine(BaseOCREngine):
    """Tesseract OCR engine implementation"""

    def __init__(self):
        self.initialized = False

    def initialize(self) -> None:
        """Initialize Tesseract engine"""
        try:
            # Tesseract is typically pre-installed, just verify it's available
            pytesseract.get_tesseract_version()
            self.initialized = True
            logging.info("Tesseract engine initialized successfully")
        except Exception as e:
            logging.error("Tesseract initialization failed: %s", str(e))
            self.initialized = False

    def is_ready(self) -> Tuple[bool, str]:
        """Check if Tesseract is ready to use"""
        if not self.initialized:
            return False, "Not initialized"
        return True, "Ready"

    def preprocess_image(self, img: Image.Image, max_size: int = -1) -> Image.Image:
        """Preprocess image for Tesseract OCR"""
        # Get max_size from settings if not provided
        if max_size == -1:
            max_size = getattr(settings, "OCR_CONFIG", {}).get(
                "TESSERACT_MAX_IMAGE_SIZE", 2048
            )

        # Convert to RGB if needed
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Get original dimensions
        width, height = img.size
        logging.info("Original image size: %dx%d", width, height)

        # Calculate new dimensions while maintaining aspect ratio
        if width > height:
            if width > max_size:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                return img
        else:
            if height > max_size:
                new_height = max_size
                new_width = int(width * (max_size / height))
            else:
                return img

        # Resize image
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        logging.info("Resized image to: %dx%d", new_width, new_height)

        return resized_img

    def extract_text(self, img: Any):
        """Extract text using Tesseract OCR. Returns (text, average_conf, tables=None) for interface compatibility."""
        if not self.is_ready()[0]:
            raise RuntimeError("Tesseract not ready")

        # Preprocess image
        processed_img = self.preprocess_image(img)

        # Extract text and confidence data
        ocr_data = pytesseract.image_to_data(
            processed_img, output_type=pytesseract.Output.DICT
        )

        # Extract text
        text = " ".join([word for word in ocr_data["text"] if word.strip()])

        # Calculate average confidence
        confidences = [
            float(conf)
            for conf, word in zip(ocr_data["conf"], ocr_data["text"])
            if word.strip() and float(conf) != -1
        ]
        average_conf = (
            round(sum(confidences) / len(confidences), 3) if confidences else None
        )

        logging.info("Tesseract extracted text: '%s'", text)
        logging.info("Tesseract average confidence: %s", str(average_conf))

        return text, average_conf, None
