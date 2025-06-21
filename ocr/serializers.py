from rest_framework import serializers

allowed_models = {'Tesseract', 'PaddleOCR'}

class OCRImageSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True)
    model = serializers.CharField(required=False, default='Tesseract')

    def validate_model(self, value):
        if value not in allowed_models:
            raise serializers.ValidationError(
                f"Invalid model name. Valid options are: {', '.join(sorted(allowed_models))}")
        return value 