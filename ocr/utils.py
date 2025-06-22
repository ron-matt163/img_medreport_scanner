import gc
import logging
import psutil
import os
from typing import Optional


def log_memory_usage(prefix: str = ""):
    """Log current memory usage for debugging"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    memory_percent = process.memory_percent()

    logging.info(
        "%sMemory usage: RSS=%.2f MB, VMS=%.2f MB, Percent=%.1f%%",
        f"{prefix} " if prefix else "",
        memory_info.rss / 1024 / 1024,
        memory_info.vms / 1024 / 1024,
        memory_percent,
    )


def force_garbage_collection():
    """Force garbage collection to free memory"""
    logging.info("Forcing garbage collection...")
    collected = gc.collect()
    logging.info("Garbage collection completed, collected %d objects", collected)


def check_memory_available(min_mb: int = 500) -> bool:
    """
    Check if sufficient memory is available

    Args:
        min_mb: Minimum memory required in MB

    Returns:
        True if sufficient memory is available
    """
    try:
        memory = psutil.virtual_memory()
        available_mb = memory.available / 1024 / 1024

        logging.info("Available memory: %.2f MB", available_mb)

        if available_mb < min_mb:
            logging.warning(
                "Insufficient memory available: %.2f MB < %d MB", available_mb, min_mb
            )
            return False

        return True
    except Exception as e:
        logging.warning("Could not check memory availability: %s", str(e))
        return True  # Assume OK if we can't check


def preprocess_image_safely(img, max_size: Optional[int] = None):
    """
    Safely preprocess image with memory checks

    Args:
        img: PIL Image to preprocess
        max_size: Maximum dimension size

    Returns:
        Preprocessed PIL Image
    """
    # Check memory before processing
    if not check_memory_available(min_mb=1000):
        logging.warning("Low memory detected, forcing garbage collection")
        force_garbage_collection()

    # Import here to avoid circular imports
    from .engines.ocr_engines import preprocess_image_for_paddleocr

    return preprocess_image_for_paddleocr(img, max_size)
