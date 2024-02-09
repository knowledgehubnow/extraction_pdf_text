from django.shortcuts import render, redirect,HttpResponse
import json
from django.core.serializers import serialize
from .models import *
import ast
import time
from pdfminer.high_level import extract_text
from io import BytesIO
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from rest_framework.parsers import FormParser, MultiPartParser
import uuid
from django.http import JsonResponse
from django.urls import reverse

def home_page(request):
    if request.method == "POST":
        pdf_file = request.FILES.get("pdf")  # Use request.FILES to handle file uploads
        if pdf_file:
            try:
                # Check if PDF with the same name exists
                pdf_data = AnalyzePDF.objects.filter(pdf_name=pdf_file).first()
                print(pdf_data)

                if pdf_data is None:
                    # Convert the InMemoryUploadedFile to a BytesIO object
                    pdf_content = pdf_file.read()
                    
                    # Extract text using pdfminer
                    all_text = extract_text(BytesIO(pdf_content))
                    print(all_text)

                    # Save to the database
                    pdf_data = AnalyzePDF(pdf_name=pdf_file, pdf_file=pdf_file, pdf_text=all_text)
                    pdf_data.save()

                    return render(request, "pdf_upload.html", {
                        "pdf_name": pdf_file,
                        "all_text": all_text,
                    })
                else:
                    return render(request, "pdf_upload.html", {
                        "message": "PDF already exists with the same name.",
                        "tag": "danger",
                    })
            except Exception as e:
                print(f"Error reading PDF: {e}")
                return render(request, "pdf_upload.html", {
                    "message": "Something went wrong. Please try again.",
                    "tag": "danger",
                })
        else:
            print("No PDF file uploaded")
            return render(request, "pdf_upload.html", {
                "message": "No PDF file uploaded",
                "tag": "danger",
            })
    return render(request,"pdf_upload.html")

def image_analysis(request):
    if request.method == "POST":
        img = request.FILES.get("image")
        print(img)
        try:
            # Check if an image with the same name exists
            image_data = ImageRecognition.objects.get(name=img)
            # If exists, return the existing data
            return render(request, "upload_image.html", {
                "message": "Image already exists with this name and this image data shown below.",
                "tag": "info",
                "image_data":image_data,
                "face_analysis": ast.literal_eval(image_data.dominant_emotion)
            })
        except ImageRecognition.DoesNotExist:
            # If not exists, perform face analysis and save the new image data
            if img:
                # Save the uploaded image to a temporary file
                with open("temp_image.jpg", "wb") as f:
                    for chunk in img.chunks():
                        f.write(chunk)

                # Restrict TensorFlow to use only CPU
                tf.config.set_visible_devices([], 'GPU')

                # Analyze image using DeepFace
                face_analysis = DeepFace.analyze(img_path="temp_image.jpg", enforce_detection=False, detector_backend='mtcnn')
                emotions = [data['dominant_emotion'] for data in face_analysis]

                # Save analysis results to the database
                image_recognition = ImageRecognition(name=img, image=img,image_analysis_data = face_analysis,dominant_emotion=str(emotions))
                image_recognition.save()
                image_data = ImageRecognition.objects.get(name=img)
                # You may want to delete the temporary file after analysis
                os.remove("temp_image.jpg")

                return render(request, "upload_image.html", {
                    "face_analysis": emotions,
                    "image_data":image_data,
                })
            else:
                pass

    return render(request, "upload_image.html")

def analized_image_list(request):
    all_data = ImageRecognition.objects.all()
    return render(request,"analize_image_list.html",{
        "all_data":all_data
    })

def analyze_pdf(request):
    if request.method == "POST":
        pdf_file = request.FILES.get("pdf")  # Use request.FILES to handle file uploads
        if pdf_file:
            try:
                # Check if PDF with the same name exists
                pdf_data = AnalyzePDF.objects.filter(pdf_name=pdf_file).first()
                print(pdf_data)

                if pdf_data is None:
                    # Convert the InMemoryUploadedFile to a BytesIO object
                    pdf_content = pdf_file.read()
                    
                    # Extract text using pdfminer
                    all_text = extract_text(BytesIO(pdf_content))
                    print(all_text)

                    # Save to the database
                    pdf_data = AnalyzePDF(pdf_name=pdf_file, pdf_file=pdf_file, pdf_text=all_text)
                    pdf_data.save()

                    return render(request, "pdf_upload.html", {
                        "pdf_name": pdf_file,
                        "all_text": all_text,
                    })
                else:
                    return render(request, "pdf_upload.html", {
                        "message": "PDF already exists with the same name.",
                        "tag": "danger",
                    })
            except Exception as e:
                print(f"Error reading PDF: {e}")
                return render(request, "pdf_upload.html", {
                    "message": "Something went wrong. Please try again.",
                    "tag": "danger",
                })
        else:
            print("No PDF file uploaded")
            return render(request, "pdf_upload.html", {
                "message": "No PDF file uploaded",
                "tag": "danger",
            })

    return render(request, "pdf_upload.html")


def analyzed_pdf_list(request):
    all_pdf = AnalyzePDF.objects.all()
    return render(request,"analized_pdf_list.html",{
        "all_pdf":all_pdf
    })

def analyzed_pdf_view(request,pdf_id):
    pdf = AnalyzePDF.objects.get(id = pdf_id)
    return render(request,"analyzed_pdf_view.html",{
        "pdf":pdf
    })


#Image analysis API code start ******************************************

class ImageAnalysisView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ImageSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                image_file = serializer.validated_data['image']
            except KeyError:
                error_response = {
                    "message": "Image field is required. Please check image field correctly defined.",
                }
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)      
            
            try:
                image_data = ImageRecognition.objects.get(name=image_file)
                image_data = {
                    "message":"Image already with this name."
                }
                return Response(
                    image_data,
                    status=status.HTTP_409_CONFLICT,
                    content_type="application/json"  # Set content type to application/json
                )
            except ImageRecognition.DoesNotExist:
                if image_file:
                    # Check image size
                    if hasattr(image_file, 'size') and image_file.size > 10 * 1024 * 1024:
                        message = "Image size should be less than 10MB."
                        return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Save the uploaded image to a temporary file
                    with open("temp_image.jpg", "wb") as f:
                        for chunk in image_file.chunks():
                            f.write(chunk)

                    # Restrict TensorFlow to use only CPU
                    tf.config.set_visible_devices([], 'GPU')

                    # Analyze image using DeepFace
                    face_analysis = DeepFace.analyze(img_path="temp_image.jpg", enforce_detection=False, detector_backend='mtcnn')
                    emotions = [data['dominant_emotion'] for data in face_analysis]

                    # Save analysis results to the database
                    image_recognition = ImageRecognition(name=image_file, image=image_file,image_analysis_data = face_analysis,dominant_emotion=str(emotions))
                    image_recognition.save()
                    image_data = ImageRecognition.objects.get(name=image_file)
                    # You may want to delete the temporary file after analysis
                    os.remove("temp_image.jpg")

                    serializer = ImageDataSerializer(image_data)  # Use your VideoDataSerializer to serialize the instance
                    serialized_data = serializer.data
                    return Response(
                        serialized_data,
                        status=status.HTTP_200_OK
                    )
                else:
                    image_data = {
                        "message":"Image not found,Please upload an image."
                    }
                    return Response(
                        image_data,
                        status=status.HTTP_404_NOT_FOUND,
                        content_type="application/json" 
                    )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# Analysed video list api code **************************
class AnalysedImageListView(APIView):
    def get(self,request):
        all_data = ImageRecognition.objects.all()
        serializer = ImageDataListSerializer(all_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

            