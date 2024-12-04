from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from PIL import Image
from .models import UplodedImage
import os
from django.conf import settings
from django.core.exceptions import ValidationError

class Image_compressor_view(View):
    def get(self,request):
        return render(request,"indexform.html")
    
    def validate_extension(self,Image_file_path):
        all_extensions=['jpg','jpeg','png','gif']
        ext=str(Image_file_path).split('.')[-1].lower()
        if ext not in all_extensions:
            raise ValidationError(f"unsupported file extention {ext}")
        
    
    def post(self,request):

        file_path=request.FILES.get('images')
        self.validate_extension(file_path)
        print("Image path=>",file_path)

        obj=UplodedImage.objects.create(image=file_path)
        obj.save()


        compression_option=request.POST.get('compressionOption')
        max_size=request.POST.get('max_size_value')
        quality=request.POST.get('quality_value')

        print("======>",max_size,quality,compression_option)


        
        # compressed_path = self.compress(obj.image)
        # if compressed_path:
        #     obj.compressed_image.save(
        #         os.path.basename(compressed_path),
        #         open(compressed_path, 'rb')
        #     )
        #     obj.save()
        #     return render(request, "sucess.html", {'filepath': obj.compressed_image.url})
        return HttpResponse("<h1>Error</h1>")

       
    def compress(self, image_field):
        try:
            original_image_path = image_field.path
            compressed_dir = os.path.join(settings.MEDIA_ROOT, 'compressed')
            os.makedirs(compressed_dir, exist_ok=True)
            compressed_image_path = os.path.join(compressed_dir, os.path.basename(original_image_path))

    
            img = Image.open(original_image_path)
            format=img.format


            if format in ['JPEG','JPG']:
                img.save(compressed_image_path,'JPEG',quality=100,optimize=True)
            elif format == 'PNG':
                img.save(compressed_image_path,'PNG',optimize=True)
            elif format=='GIF':
                img.save(compressed_image_path,'GIF',save_all=True,optimize=True)
            else:
                return ValueError(f"unsupported format {format}")
            return compressed_image_path
        
        except Exception as e:
            print("Error compressing image:", e)
            return None


class Image_Resizer_view(View):
    def get():
        pass
    def post():
        pass


class Image_Crop_view(View):
    def get():
        pass
   
    def post():
        pass


# Create your views here.
