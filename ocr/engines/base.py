"""
Base OCR Engine Module

This module defines the abstract base class for OCR engines.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Any
from PIL import Image


class BaseOCREngine(ABC):
    """Base class for OCR engines"""

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the OCR engine"""
        pass

    @abstractmethod
    def is_ready(self) -> Tuple[bool, str]:
        """Check if the engine is ready to use"""
        pass

    @abstractmethod
    def extract_text(self, img: Any):
        """Extract text from image and return (text, confidence, tables) if available. For table engines, text is the full OCR text, and tables is a list of HTML tables if present."""
        pass

    @abstractmethod
    def preprocess_image(self, img: Image.Image, max_size: int = -1) -> Image.Image:
        """Preprocess image for optimal OCR performance"""
        pass
