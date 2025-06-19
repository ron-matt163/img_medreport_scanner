from typing import Tuple, Any

import pytesseract
from paddleocr import PaddleOCR
import numpy as np
import logging
import os

# Initialize PaddleOCR once as a module-level singleton
paddle_ocr = None
paddle_ocr_init_error = None
_initialization_attempted = False

def initialize_paddle_ocr():
    """Initialize PaddleOCR synchronously during service startup"""
    global paddle_ocr, paddle_ocr_init_error, _initialization_attempted
    
    if _initialization_attempted:
        logging.info("PaddleOCR initialization already attempted, skipping...")
        return
    
    _initialization_attempted = True
    
    if paddle_ocr is not None:
        logging.info("PaddleOCR already initialized, skipping...")
        return
    
    try:
        logging.info("Initializing PaddleOCR during service startup...")
        # Set environment variable to prevent re-downloading models
        os.environ['PADDLE_HOME'] = '/home/appuser/.paddlex'
        paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en')
        logging.info("PaddleOCR initialization completed successfully")
    except Exception as e:
        logging.error("PaddleOCR initialization failed: %s", str(e))
        paddle_ocr_init_error = str(e)

def get_paddle_ocr():
    return paddle_ocr

def is_paddle_ocr_ready():
    """Check if PaddleOCR is ready to use"""
    global paddle_ocr, paddle_ocr_init_error
    
    if paddle_ocr_init_error:
        return False, f"Initialization failed: {paddle_ocr_init_error}"
    
    if paddle_ocr is None:
        return False, "Not initialized"
    
    return True, "Ready"

def ocr_tesseract(img: Any) -> Tuple[str, float]:
    ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    text = ' '.join([word for word in ocr_data['text'] if word.strip()])
    confidences = [
        float(conf)
        for conf, word in zip(ocr_data['conf'], ocr_data['text'])
        if word.strip() and float(conf) != -1
    ]
    average_conf = round(sum(confidences) / len(confidences), 3) if confidences else None
    return text, average_conf

def ocr_paddleocr(img: Any) -> Tuple[str, float]:
    # Check if PaddleOCR is ready
    ready, status = is_paddle_ocr_ready()
    if not ready:
        raise RuntimeError(f"PaddleOCR not ready: {status}")
    
    try:
        ocr = get_paddle_ocr()
        
        logging.info("Converting image format...")
        if hasattr(img, 'mode') and img.mode != 'RGB':
            img = img.convert('RGB')
        img_np = np.array(img)
        logging.info("Image converted to numpy array, shape: %s, dtype: %s", img_np.shape, img_np.dtype)
        
        logging.info("Running PaddleOCR prediction...")
        try:
            result = ocr.predict(img_np)
            logging.info("PaddleOCR predict() completed successfully")
        except Exception as predict_error:
            logging.error("PaddleOCR predict() failed: %s", str(predict_error), exc_info=True)
            raise RuntimeError(f"PaddleOCR prediction failed: {str(predict_error)}")
        
        logging.info("PaddleOCR result structure: %s", str(result))
        
        words = []
        confidences = []
        if result:
            for line in result:
                logging.info("Processing line: %s", str(line))
                if line:  # Check if line exists
                    for word_info in line:
                        if word_info and len(word_info) >= 2:  # Ensure word_info has required structure
                            word = word_info[1][0]
                            conf = word_info[1][1]
                            words.append(word)
                            confidences.append(conf)
                            logging.info("Extracted word: '%s' with confidence: %f", word, conf)
        
        text = ' '.join(words)
        average_conf = round(sum(confidences) / len(confidences), 3) if confidences else None
        logging.info("Final extracted text: '%s'", text)
        logging.info("Average confidence: %s", str(average_conf))
        return text, average_conf
        
    except Exception as e:
        logging.error("Error in PaddleOCR processing: %s", str(e), exc_info=True)
        raise RuntimeError(f"PaddleOCR processing failed: {str(e)}")

def perform_ocr(img: Any, model_name: str) -> Tuple[str, float]:
    if model_name == 'Tesseract':
        return ocr_tesseract(img)
    elif model_name == 'PaddleOCR':
        return ocr_paddleocr(img)
    else:
        raise ValueError(f"Unknown OCR model: {model_name}")