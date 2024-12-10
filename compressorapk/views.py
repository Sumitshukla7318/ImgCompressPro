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
    def get(self,request):
        return render(request,"resizer_index.html")
    
    def validate_extension(image):
        ext=str(image).split('.')
        if ext[-1].lower() not in ['png','jpeg','gfg','jpg']:
            return ValidationError(f"unsupported file extension {ext}")
       
    
    def post(self,request):
        file_path=request.FILES.get('image')
        
        self.validate_extension(file_path)
        height=request.POST.get('height')
        width=request.POST.get('width')
        
        obj=UplodedImage.objects.create(image=file_path)
        obj.save()

        resized_path=self.resized(obj.image,height,width)
        
        if resized_path:
             obj.resized_image.save(
                os.path.basename(resized_path),
                open(resized_path, 'rb')
            )
             obj.save()
             return render(request, "resized_sucess.html", {'filepath': obj.resized_image.url,'oldpath':obj.image.url})
        return HttpResponse("<h1>Error</h1>")
    
 
    def resized(self, image_field, height, width):
          try:
            original_image_path = image_field.path
            resized_dir = os.path.join(settings.MEDIA_ROOT, 'resized')
            os.makedirs(resized_dir, exist_ok=True)
            resized_image_path = os.path.join(resized_dir, os.path.basename(original_image_path))
            print(resized_image_path)
        
            with Image.open(original_image_path) as img:
                img_resized = img.resize((int(width), int(height)), Image.Resampling.LANCZOS)
                img_resized.save(resized_image_path, quality=95, optimize=True)
            
            return resized_image_path
          except Exception as e:
            print(f"Error resizing image: {e}")
            return None



class PngToJpgConverter(View):
    pass

class JpgToPngConverter(View):
    pass

class JpgToGifConverter(View):
    pass

class PdfToJpgConverter(View):
    pass

class PdfToPngConverter(View):
    pass

        
        




