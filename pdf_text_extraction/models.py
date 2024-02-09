from django.db import models
from django.conf import settings
import ast
import json
from django.utils import timezone
# Create your models here.


class ImageRecognition(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    image_analysis_data = models.JSONField(null=True, blank=True)
    dominant_emotion = models.CharField(max_length=255, null=True, blank=True)

    def images_list(self):
        return ast.literal_eval(self.dominant_emotion)


class AnalyzePDF(models.Model):
    pdf_name = models.CharField(max_length=255, null=True, blank=True)
    pdf_file = models.FileField(upload_to='pdf/', null=True, blank=True)
    pdf_text = models.TextField()

    def __str__(self):
        return self.pdf_name
    

    
