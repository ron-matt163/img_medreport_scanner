import logging
import os
import numpy as np
from typing import Tuple, Any
from PIL import Image
from django.conf import settings
from paddleocr import PaddleOCR
from .base import BaseOCREngine
from ..utils import log_memory_usage, check_memory_available, force_garbage_collection


class PaddleOCREngine(BaseOCREngine):
    """PaddleOCR engine implementation"""

    def __init__(self):
        self.ocr = None
        self.initialized = False
        self.init_error = None

    def initialize(self) -> None:
        """Initialize PaddleOCR engine"""
        if self.initialized:
            logging.info("PaddleOCR already initialized, skipping...")
            return

        try:
            logging.info("Initializing PaddleOCR during service startup...")
            # Set environment variable to prevent re-downloading models
            os.environ["PADDLE_HOME"] = "/home/appuser/.paddlex"

            self.ocr = PaddleOCR(use_angle_cls=True, lang="en")

            self.initialized = True
            logging.info("PaddleOCR initialization completed successfully")
        except Exception as e:
            logging.error("PaddleOCR initialization failed: %s", str(e))
            self.init_error = str(e)
            self.initialized = False

    def is_ready(self) -> Tuple[bool, str]:
        """Check if PaddleOCR is ready to use"""
        if self.init_error:
            return False, f"Initialization failed: {self.init_error}"

        if not self.initialized or self.ocr is None:
            return False, "Not initialized"

        return True, "Ready"

    def preprocess_image(self, img: Image.Image, max_size: int = -1) -> Image.Image:
        """Preprocess image for PaddleOCR"""
        # Get max_size from settings if not provided
        if max_size == -1:
            max_size = getattr(settings, "OCR_CONFIG", {}).get(
                "PADDLEOCR_MAX_IMAGE_SIZE", 1024
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

    def _extract_text_with_rec_scores(self, result_obj):
        """Extract text and confidence scores from result object with rec_scores"""
        extracted_words = []
        extracted_confs = []

        rec_scores = result_obj["rec_scores"]
        logging.info("Found rec_scores with length: %d", len(rec_scores))

        # Look for rec_texts specifically (this is where the actual text is)
        if "rec_texts" in result_obj:
            rec_texts = result_obj["rec_texts"]
            logging.info("Found rec_texts with length: %d", len(rec_texts))

            # Match rec_texts with rec_scores
            if len(rec_texts) == len(rec_scores):
                # Perfect match - one score per text segment
                for text_segment, score in zip(rec_texts, rec_scores):
                    if isinstance(text_segment, str) and text_segment.strip():
                        # Split text segment into individual words
                        words = text_segment.split()
                        for word in words:
                            if word.strip():
                                extracted_words.append(word.strip())
                                extracted_confs.append(score)
                return extracted_words, extracted_confs
            elif len(rec_scores) > 0:
                # Use average score for all text segments
                avg_score = sum(rec_scores) / len(rec_scores)
                for text_segment in rec_texts:
                    if isinstance(text_segment, str) and text_segment.strip():
                        words = text_segment.split()
                        for word in words:
                            if word.strip():
                                extracted_words.append(word.strip())
                                extracted_confs.append(avg_score)
                return extracted_words, extracted_confs

        logging.warning("Found rec_scores but no matching rec_texts field")
        return extracted_words, extracted_confs

    def _extract_text_from_dict(self, result_obj):
        """Extract text from dictionary result object"""
        extracted_words = []
        extracted_confs = []

        # Look for rec_scores specifically
        if "rec_scores" in result_obj:
            words, confs = self._extract_text_with_rec_scores(result_obj)
            extracted_words.extend(words)
            extracted_confs.extend(confs)

        return extracted_words, extracted_confs

    def _extract_text_from_result(self, result_obj):
        """Recursively extract text from PaddleOCR result"""
        extracted_words = []
        extracted_confs = []

        if isinstance(result_obj, list):
            for item in result_obj:
                words, confs = self._extract_text_from_result(item)
                extracted_words.extend(words)
                extracted_confs.extend(confs)
        elif isinstance(result_obj, dict):
            words, confs = self._extract_text_from_dict(result_obj)
            extracted_words.extend(words)
            extracted_confs.extend(confs)

        return extracted_words, extracted_confs

    def _log_extraction_results(self, words, confidences):
        """Log the extracted words and confidence scores"""
        logging.info(
            "Extracted %d words with %d confidence scores", len(words), len(confidences)
        )
        for i, (word, conf) in enumerate(zip(words, confidences)):
            logging.info("Word %d: '%s' with confidence: %f", i + 1, word, conf)

    def extract_text(self, img: Any) -> Tuple[str, float]:
        """Extract text using PaddleOCR"""
        if not self.is_ready()[0]:
            raise RuntimeError(f"PaddleOCR not ready: {self.is_ready()[1]}")

        try:
            # Log memory usage before processing
            log_memory_usage("Before PaddleOCR preprocessing")

            # Check memory availability
            if not check_memory_available(min_mb=1000):
                logging.warning("Low memory detected, forcing garbage collection")
                force_garbage_collection()

            logging.info("Preprocessing image for PaddleOCR...")
            processed_img = self.preprocess_image(img)

            # Convert to numpy array
            img_np = np.array(processed_img)
            logging.info(
                "Image converted to numpy array, shape: %s, dtype: %s",
                img_np.shape,
                img_np.dtype,
            )

            # Log memory usage before prediction
            log_memory_usage("Before PaddleOCR prediction")

            # Run prediction
            logging.info("Running PaddleOCR prediction...")
            try:
                result = self.ocr.predict(img_np)
                logging.info("PaddleOCR predict() completed successfully")
            except Exception as predict_error:
                logging.error(
                    "PaddleOCR predict() failed: %s", str(predict_error), exc_info=True
                )
                raise RuntimeError(f"PaddleOCR prediction failed: {str(predict_error)}")

            # Log memory usage after prediction
            log_memory_usage("After PaddleOCR prediction")

            logging.info("PaddleOCR result structure: %s", str(result))

            # Extract text using the recursive function
            words, confidences = self._extract_text_from_result(result)

            # Log extraction results
            # self._log_extraction_results(words, confidences)

            text = " ".join(words)
            average_conf = (
                round(sum(confidences) / len(confidences), 3) if confidences else None
            )
            logging.info("Final extracted text: '%s'", text)
            logging.info("Average confidence: %s", str(average_conf))

            # Force garbage collection after processing
            force_garbage_collection()
            log_memory_usage("After garbage collection")

            return text, average_conf
        except Exception as e:
            logging.error("Error in PaddleOCR processing: %s", str(e), exc_info=True)
            raise RuntimeError(f"PaddleOCR processing failed: {str(e)}")
