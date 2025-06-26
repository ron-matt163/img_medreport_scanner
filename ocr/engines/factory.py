from typing import Dict, Type
from .base import BaseOCREngine
from .tesseract_engine import TesseractEngine
from .paddle_ocr_engine import PaddleOCREngine
from .paddle_table_ocr_engine import PaddleTableOCREngine


class OCREngineFactory:
    """Factory for creating and managing OCR engines"""

    _engines: Dict[str, BaseOCREngine] = {}

    @classmethod
    def get_engine(cls, engine_name: str) -> BaseOCREngine:
        """Get or create an OCR engine by name"""
        if engine_name not in cls._engines:
            cls._engines[engine_name] = cls._create_engine(engine_name)

        return cls._engines[engine_name]

    @classmethod
    def _create_engine(cls, engine_name: str) -> BaseOCREngine:
        """Create a new OCR engine instance"""
        if engine_name.lower() == "tesseract":
            engine = TesseractEngine()
        elif engine_name.lower() == "paddleocr":
            engine = PaddleOCREngine()
        elif engine_name.lower() == "paddletable":
            engine = PaddleTableOCREngine()
        else:
            raise ValueError(f"Unknown OCR engine: {engine_name}")

        # Initialize the engine
        engine.initialize()
        return engine

    @classmethod
    def initialize_all_engines(cls) -> None:
        """Initialize all supported engines"""
        cls.get_engine("Tesseract")
        cls.get_engine("PaddleOCR")
        cls.get_engine("PaddleTable")

    @classmethod
    def get_available_engines(cls) -> list:
        """Get list of available engine names"""
        return ["Tesseract", "PaddleOCR", "PaddleTable"]
