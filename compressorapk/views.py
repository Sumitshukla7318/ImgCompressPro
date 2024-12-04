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

        
        if max_size:
            compressed_path=self.compress_by_size(obj.image,max_size)
        elif quality:
            compressed_path=self.compress_by_quality(obj.image,quality)
        else:
            compressed_path=self.compress(obj.image)
        


        
        # compressed_path = self.compress(obj.image)
        if compressed_path:
            obj.compressed_image.save(
                os.path.basename(compressed_path),
                open(compressed_path, 'rb')
            )
            obj.save()
            return render(request, "sucess.html", {'filepath': obj.compressed_image.url,'oldpath':obj.image.url})
        return HttpResponse("<h1>Error</h1>")

       
    def compress_by_size(self,imagefield,max_size):
        try:
            original_image_path=imagefield.path
            compressed_dir = os.path.join(settings.MEDIA_ROOT, 'compressed')
            os.makedirs(compressed_dir, exist_ok=True)
            compressed_image_path = os.path.join(compressed_dir, os.path.basename(original_image_path))

            img=Image.open(original_image_path)
            format=img.format
            max_size=int(max_size)*1024

            quality=85
            step=5
            while True:
                if format in ['JPEG', 'JPG']:
                    img.save(compressed_image_path,'JPEG',quality=quality,optimize=True)
                elif format=='PNG':
                    img.save(compressed_image_path,"PNG",optimize=True,compress_level=int(9 - (quality / 100) * 9))
                elif format=="GIF":
                    img.save(compressed_image_path,"GIF",save_all=True,optimize=True)
                else:
                    raise ValueError(f"unsoported format {format}")
                
                if os.path.getsize(compressed_image_path)<=max_size or quality<=10:
                    break
                quality-=step
            return compressed_image_path
        except Exception as e:
            print("error=>",e)
            return None
        
    
    def compress_by_quality(self,imagefield,quality):
        try:
            original_image_path=imagefield.path
            compressed_dir = os.path.join(settings.MEDIA_ROOT, 'compressed')
            os.makedirs(compressed_dir, exist_ok=True)
            compressed_image_path = os.path.join(compressed_dir, os.path.basename(original_image_path))
            
            img=Image.open(original_image_path)
            frmt=img.format

            quality=int(quality)

            if frmt in ['JPEG', 'JPG']:
                img.save(compressed_image_path, 'JPEG', quality=quality, optimize=True)
            elif frmt =='PNG':
                img.save(compressed_image_path, 'PNG', optimize=True, compress_level=9)
            elif frmt =='GIF':
                img.save(compressed_image_path, 'GIF', save_all=True, optimize=True)
            else:
                raise ValueError(f"unsoported format {format}")
            
            return compressed_image_path
        
        except Exception as e:
            print("error",e)
            return None
            

                 

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
