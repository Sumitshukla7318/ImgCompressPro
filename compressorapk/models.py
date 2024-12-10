from django.db import models

class UplodedImage(models.Model):
    image=models.ImageField(upload_to='uploads/')
    compressed_image=models.ImageField(upload_to='compressed/',blank=True,null=True)
    resized_image=models.ImageField(upload_to='resized/',blank=True,null=True)
    uploaded_at=models.DateTimeField(auto_now_add=True)
    

# Create your models here.
