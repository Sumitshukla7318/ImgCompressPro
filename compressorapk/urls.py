from django.urls import path
from . import views

urlpatterns = [
    path('',views.Image_compressor_view.as_view(),name='upload'),
    path('resizer/',views.Image_Resizer_view.as_view(),name='resizer'),
    path('change_format/',views.ImageFormatConverter.as_view(),name='change_format'),
]
