from rest_framework import serializers
from .models import *

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageRecognition
        fields = ('image',)

class ImageDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageRecognition
        fields = "__all__"

class ImageDataListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageRecognition
        fields = "__all__"




