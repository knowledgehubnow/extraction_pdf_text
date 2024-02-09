from django.contrib import admin
from django.urls import path,include
from . import views
from .views import *

urlpatterns = [
    path('',views.home_page,name = "home_page"),
    path('image/processing/',views.image_analysis,name = "image_analysis"),
    path('analized/image/list/',views.analized_image_list,name = "analized_image_list"),
    path('analyze/pdf/',views.analyze_pdf,name = "analyze_pdf"),
    path('analyzed/pdf/list/',views.analyzed_pdf_list,name = "analyzed_pdf_list"),
    path('analyzed/pdf/view/<int:pdf_id>/',views.analyzed_pdf_view,name = "analyzed_pdf_view"),
    
    path('analysed/image/list/', AnalysedImageListView.as_view()),
]