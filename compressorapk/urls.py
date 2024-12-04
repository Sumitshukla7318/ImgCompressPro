from django.urls import path
from . import views

urlpatterns = [
    path('',views.Image_compressor_view.as_view(),name='upload'),
]
