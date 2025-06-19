from rest_framework import serializers

class OCRImageSerializer(serializers.Serializer):
    image = serializers.ImageField() 