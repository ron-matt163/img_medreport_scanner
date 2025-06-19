"""OCR API views for medical report scanning."""

import time
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PIL import Image

from .serializers import OCRImageSerializer
from .ocr_engines import perform_ocr

class OCRView(APIView):
    """API view for OCR processing of medical report images."""
    def post(self, request):
        """Process OCR request for image text extraction."""
        
        serializer = OCRImageSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data['image']
            model = serializer.validated_data.get('model', 'Tesseract')
            img = Image.open(image)
            start_time = time.time()
            
            try:
                text, average_conf = perform_ocr(img, model)
            except RuntimeError as e:
                if "PaddleOCR not ready" in str(e):
                    return Response({
                        'error': str(e),
                        'status': 'initializing'
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                else:
                    logging.error("OCR error: %s", str(e))
                    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except (ImportError, ValueError, OSError) as e:
                logging.error("OCR error: %s", str(e))
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            latency = time.time() - start_time
            
            logging.info("Extracted text: %s", text)
            logging.info("OCR parsing latency: %.3f seconds", latency)
            logging.info("Average confidence: %.2f", average_conf)
            
            return Response({'text': text, 'average_confidence': average_conf})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)