from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import OCRImageSerializer
from PIL import Image
import pytesseract

class OCRView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OCRImageSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data['image']
            img = Image.open(image)
            text = pytesseract.image_to_string(img)
            return Response({'text': text})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)