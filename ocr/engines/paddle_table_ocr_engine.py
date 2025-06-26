import logging
from typing import Tuple, Any
from PIL import Image
import numpy as np
from paddleocr import TableRecognitionPipelineV2
from .base import BaseOCREngine
from ..utils import log_memory_usage, check_memory_available, force_garbage_collection


class PaddleTableOCREngine(BaseOCREngine):
    """PaddleOCR Table Recognition engine implementation using TableRecognitionPipelineV2."""

    def __init__(self):
        self.pipeline = None
        self.initialized = False
        self.init_error = None

    def initialize(self) -> None:
        if self.initialized:
            logging.info("PaddleTableOCREngine already initialized, skipping...")
            return
        try:
            logging.info(
                "Initializing TableRecognitionPipelineV2 for table extraction..."
            )
            # Initialize with shared models - it will use models from shared volume if they exist
            self.pipeline = TableRecognitionPipelineV2()
            self.initialized = True
            logging.info("PaddleTableOCREngine initialization completed successfully")
        except Exception as e:
            logging.error("PaddleTableOCREngine initialization failed: %s", str(e))
            self.init_error = str(e)
            self.initialized = False

    def is_ready(self) -> Tuple[bool, str]:
        if self.init_error:
            return False, f"Initialization failed: {self.init_error}"
        if not self.initialized or self.pipeline is None:
            return False, "Not initialized"
        return True, "Ready"

    def preprocess_image(self, img: Image.Image, max_size: int = -1) -> Image.Image:
        # Get max_size from settings if not provided
        if max_size == -1:
            max_size = 2048  # Limit table images to 2048px max dimension

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
        """Extract text and tables using TableRecognitionPipelineV2. Returns (text, average_conf, tables)."""
        if not self.is_ready()[0]:
            raise RuntimeError(f"PaddleTableOCREngine not ready: {self.is_ready()[1]}")

        try:
            # Log memory usage before processing
            log_memory_usage("Before PaddleTable preprocessing")

            # Check memory availability
            if not check_memory_available(min_mb=2000):
                logging.warning("Low memory detected, forcing garbage collection")
                force_garbage_collection()

            processed_img = self.preprocess_image(img)

            # Convert to numpy array
            if isinstance(processed_img, Image.Image):
                img_np = np.array(processed_img)
            else:
                img_np = processed_img

            # Log memory usage before prediction
            log_memory_usage("Before PaddleTable prediction")

            output = self.pipeline.predict(img_np)

            # Log memory usage after prediction
            log_memory_usage("After PaddleTable prediction")

            tables = []
            all_texts = []
            all_scores = []

            for res in output:
                res_obj = getattr(res, "res", res)
                # Extract tables
                table_res_list = res_obj.get("table_res_list", [])
                for table in table_res_list:
                    html = table.get("pred_html")
                    if html:
                        tables.append(html)
                    # Extract cell texts for full text
                    ocr_pred = table.get("table_ocr_pred", {})
                    rec_texts = ocr_pred.get("rec_texts", [])
                    rec_scores = ocr_pred.get("rec_scores", [])
                    all_texts.extend([t for t in rec_texts if t])
                    all_scores.extend(
                        [float(s) for s in rec_scores if isinstance(s, (int, float))]
                    )

            text = " ".join(all_texts)
            average_conf = (
                round(sum(all_scores) / len(all_scores), 3) if all_scores else None
            )
            if not tables:
                tables = None

            # Force garbage collection after processing
            force_garbage_collection()
            log_memory_usage("After PaddleTable garbage collection")

            return text, average_conf, tables

        except Exception as e:
            logging.error(
                "Error in PaddleTableOCREngine processing: %s", str(e), exc_info=True
            )
            # Force garbage collection on error
            force_garbage_collection()
            raise RuntimeError(f"PaddleTableOCREngine processing failed: {str(e)}")
