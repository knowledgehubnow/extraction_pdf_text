from django.contrib import admin
from django.urls import path,include
from . import views
from .views import *

urlpatterns = [
    path('',views.home_page,name = "home_page"),
    path('analyzed/pdf/list/',views.analyzed_pdf_list,name = "analyzed_pdf_list"),
    path('analyzed/pdf/view/<int:pdf_id>/',views.analyzed_pdf_view,name = "analyzed_pdf_view"),
]