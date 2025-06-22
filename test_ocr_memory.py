#!/usr/bin/env python3
"""
Test script to verify OCR memory management improvements.
Run this script to test the OCR functionality with memory monitoring.
"""

import os
import sys
import django
from PIL import Image
import numpy as np

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "img_medreport_scanner.settings")
django.setup()

from ocr.engines.ocr_engines import perform_ocr, preprocess_image_for_paddleocr
from ocr.utils import log_memory_usage, check_memory_available


def create_test_image(width=2000, height=1500):
    """Create a test image with text for OCR testing"""
    # Create a white background
    img_array = np.ones((height, width, 3), dtype=np.uint8) * 255

    # Add some text-like patterns (simple rectangles to simulate text)
    for i in range(0, height, 100):
        for j in range(0, width, 200):
            img_array[i : i + 20, j : j + 150] = 0  # Black rectangles

    return Image.fromarray(img_array)


def test_ocr_memory():
    """Test OCR with memory monitoring"""
    print("=== OCR Memory Management Test ===")

    # Check initial memory
    log_memory_usage("Initial")
    check_memory_available()

    # Create a large test image
    print(f"\nCreating test image (2000x1500)...")
    test_img = create_test_image(2000, 1500)
    print(f"Test image created: {test_img.size}")

    # Test Tesseract
    print(f"\n--- Testing Tesseract ---")
    try:
        log_memory_usage("Before Tesseract")
        text, conf = perform_ocr(test_img, "Tesseract")
        log_memory_usage("After Tesseract")
        print(f"Tesseract result: Text length={len(text)}, Confidence={conf}")
    except Exception as e:
        print(f"Tesseract error: {e}")

    # Test PaddleOCR
    print(f"\n--- Testing PaddleOCR ---")
    try:
        log_memory_usage("Before PaddleOCR")
        text, conf = perform_ocr(test_img, "PaddleOCR")
        log_memory_usage("After PaddleOCR")
        print(f"PaddleOCR result: Text length={len(text)}, Confidence={conf}")
    except Exception as e:
        print(f"PaddleOCR error: {e}")

    # Test image preprocessing
    print(f"\n--- Testing Image Preprocessing ---")
    try:
        log_memory_usage("Before preprocessing")
        processed_img = preprocess_image_for_paddleocr(test_img)
        log_memory_usage("After preprocessing")
        print(f"Original size: {test_img.size}")
        print(f"Processed size: {processed_img.size}")
    except Exception as e:
        print(f"Preprocessing error: {e}")

    print(f"\n=== Test completed ===")


if __name__ == "__main__":
    test_ocr_memory()
