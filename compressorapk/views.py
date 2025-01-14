from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from PIL import Image
from .models import UplodedImage
import os
from django.conf import settings
from django.core.exceptions import ValidationError
import time
from pdf2image import convert_from_path
from datetime import datetime
from PIL import Image, ImageEnhance
import io
import base64

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
    
    def validate_extension(self,image):
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



class ImageFormatConverter(View):
    def get(self,request):
        return render(request,"format_converter.html")
    

    def post(self, request):
       
        image_path = request.FILES.get('inputFile')
        from_format = request.POST.get('fromFormat')
        to_format = request.POST.get('toFormat')

        if not image_path:
            return HttpResponse("No file uploaded", status=400)
        

       
        check_format = str(image_path.name).split('.')[-1].lower()
        if check_format=='jpeg':
            check_format='jpg'
        if check_format != from_format.lower():
            return HttpResponse("Error: File format does not match the selected 'from' format.", status=400)
  
        # Save the uploaded image to the database
        obj = UplodedImage.objects.create(image=image_path)
        obj.save()


        try:
          
            input_image_path = obj.image.path  
            new_image_path = None 
            # Check if the file exists
            if not os.path.exists(input_image_path):
                return HttpResponse("Error: Image file not found.", status=400)

            if str(from_format).lower() in ['jpg','jpeg']:
                if str(to_format).lower() == 'png':
                    new_image_path=self.jpg_to_png_converter(input_image_path)

                elif str(to_format).lower() == 'gif':
                    new_image_path=self.jpg_to_gif_converter(input_image_path)

                elif str(to_format).lower() == 'pdf':
                    new_image_path=self.jpg_to_pdf_converter(input_image_path)

            elif str(from_format).lower() == 'png':
                if str(to_format).lower() == 'jpg':
                   new_image_path=self.png_to_jpg_converter(input_image_path)

                elif str(to_format).lower() == 'gif':
                    new_image_path=self.png_to_gif_converter(input_image_path)

                  
                elif str(to_format).lower() == 'pdf':
                    new_image_path=self.png_to_pdf_converter(input_image_path)


            elif str(from_format).lower() == 'pdf':
                if str(to_format).lower() == 'png':
                   new_image_path=self.pdf_to_png_converter(input_image_path)

                elif str(to_format).lower() == 'gif':
                    new_image_path=self.pdf_to_gif_converter(input_image_path)

                    
                elif str(to_format).lower() == 'jpg':
                    new_image_path=self.pdf_to_jpg_converter(input_image_path)

            elif str(from_format).lower() == 'gif':
                if str(to_format).lower() == 'png':
                   new_image_path= self.gif_to_png_converter(input_image_path)

                elif str(to_format).lower() == 'pdf':
                    new_image_path=self.gif_to_pdf_converter(input_image_path)

                elif str(to_format).lower() == 'jpg':
                    new_image_path=self.gif_to_jpg_converter(input_image_path)

            if new_image_path:
                obj.converted_image.save(os.path.basename(new_image_path), open(new_image_path, 'rb'))
                obj.save()
            else:
                return HttpResponse("Error: Conversion failed or unsupported format combination.", status=400)


        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}", status=500)

        return render(request,"show_conveted_image.html",{'converted_image_url':obj.image.url,'download_url':obj.converted_image.url})
    
    def jpg_to_png_converter(self, original_image_path):
        try:
          
            converted_folder = './media/converted_folder'  
         
            if not os.path.exists(converted_folder):
                os.makedirs(converted_folder)

            # Get the filename and create the new image path
            filename = os.path.basename(original_image_path)
            name, _ = os.path.splitext(filename)
            new_image_path = os.path.join(converted_folder, f"{name}.png")

            
            with Image.open(original_image_path) as img:
                img.save(new_image_path, format='PNG')
                print(f"Converted {original_image_path} to {new_image_path}")
                return new_image_path

        except Exception as e:
            raise Exception(f"Error in jpg_to_png_converter: {str(e)}")



    def jpg_to_gif_converter(self,original_image_path):
        try:
          
            converted_folder = './media/converted_folder'  
         
            if not os.path.exists(converted_folder):
                os.makedirs(converted_folder)

          
            filename = os.path.basename(original_image_path)
            name, _ = os.path.splitext(filename)
            new_image_path = os.path.join(converted_folder, f"{name}.gif")

            
            with Image.open(original_image_path) as img:
                img.save(new_image_path, format='GIF')
                print(f"Converted {original_image_path} to {new_image_path}")
                return new_image_path

        except Exception as e:
            raise Exception(f"Error in jpg_to_gif_converter: {str(e)}")


    def jpg_to_pdf_converter(self,original_image_path):
        try:
          
            converted_folder = './media/converted_folder'  
         
            if not os.path.exists(converted_folder):
                os.makedirs(converted_folder)

            # Get the filename and create the new image path
            filename = os.path.basename(original_image_path)
            name, _ = os.path.splitext(filename)
            new_image_path = os.path.join(converted_folder, f"{name}.pdf")

            # Open and save the image as PNG
            with Image.open(original_image_path) as img:
                img.save(new_image_path, format='PDF')
                print(f"Converted {original_image_path} to {new_image_path}")
                return new_image_path

        except Exception as e:
            raise Exception(f"Error in jpg_to_pdf_converter: {str(e)}")

    
    
    
    def png_to_jpg_converter(self,original_image_path):
        try:
          
            converted_folder = './media/converted_folder'  
         
            if not os.path.exists(converted_folder):
                os.makedirs(converted_folder)

           
            filename = os.path.basename(original_image_path)
            name, _ = os.path.splitext(filename)
            new_image_path = os.path.join(converted_folder, f"{name}.jpg")

           
            with Image.open(original_image_path) as img:
                img.save(new_image_path, format='JPG')
                print(f"Converted {original_image_path} to {new_image_path}")
                return new_image_path

        except Exception as e:
            raise Exception(f"Error in png_to_jpg_converter: {str(e)}")


    def png_to_gif_converter(self,original_image_path):
        try:
          
            converted_folder = './media/converted_folder'  
         
            if not os.path.exists(converted_folder):
                os.makedirs(converted_folder)

          
            filename = os.path.basename(original_image_path)
            name, _ = os.path.splitext(filename)
            new_image_path = os.path.join(converted_folder, f"{name}.gif")

    
            with Image.open(original_image_path) as img:
                img.save(new_image_path, format='GIF')
                print(f"Converted {original_image_path} to {new_image_path}")
                return new_image_path

        except Exception as e:
            raise Exception(f"Error in png_to_gif_converter: {str(e)}")


    def png_to_pdf_converter(self,original_image_path):
        try:
          
            converted_folder = './media/converted_folder'  
         
            if not os.path.exists(converted_folder):
                os.makedirs(converted_folder)

            filename = os.path.basename(original_image_path)
            name, _ = os.path.splitext(filename)
            new_image_path = os.path.join(converted_folder, f"{name}.pdf")

            with Image.open(original_image_path) as img:
                img.save(new_image_path, format='PDF')
                print(f"Converted {original_image_path} to {new_image_path}")
                return new_image_path

        except Exception as e:
            raise Exception(f"Error in png_to_pdf_converter: {str(e)}")

    
    
    
    def pdf_to_jpg_converter(self, original_pdf_path):
        try:
            # Define the output directory
            converted_folder = './media/converted_folder'
            
            # Create output folder if it doesn't exist
            if not os.path.exists(converted_folder):
                os.makedirs(converted_folder)
    
            # Extract the base name and file name without the extension
            filename = os.path.basename(original_pdf_path)
            name, _ = os.path.splitext(filename)
    
            # Open the PDF file
            doc = fitz.open(original_pdf_path)
    
            image_paths = []
            
            # Iterate through each page of the PDF
            for i in range(doc.page_count):
                # Get the page
                page = doc.load_page(i)
    
                # Convert the page to a pixmap (an image)
                pix = page.get_pixmap()
    
                # Define the new image path
                new_image_path = os.path.join(converted_folder, f"{name}_page_{i + 1}.jpg")
    
                # Save the pixmap as a JPG file
                pix.save(new_image_path)
                image_paths.append(new_image_path)
                print(f"Saved page {i + 1} to {new_image_path}")
        
            return image_paths
        except Exception as e:
             raise Exception(f"Error in pdf_to_jpg_converter: {str(e)}")
    
    def pdf_to_gif_converter(self,original_image_path):
        try:
          
            converted_folder = './media/converted_folder'  
         
            if not os.path.exists(converted_folder):
                os.makedirs(converted_folder)

           
            filename = os.path.basename(original_image_path)
            name, _ = os.path.splitext(filename)
            new_image_path = os.path.join(converted_folder, f"{name}.gif")

            # Open and save the image as PNG
            with Image.open(original_image_path) as img:
                img.save(new_image_path, format='GIF')
                print(f"Converted {original_image_path} to {new_image_path}")
                return new_image_path

        except Exception as e:
            raise Exception(f"Error in pdf_to_gif_converter: {str(e)}")


    def pdf_to_png_converter(self,original_image_path):
        try:
          
            converted_folder = './media/converted_folder'  
         
            if not os.path.exists(converted_folder):
                os.makedirs(converted_folder)

           
            filename = os.path.basename(original_image_path)
            name, _ = os.path.splitext(filename)
            new_image_path = os.path.join(converted_folder, f"{name}.png")

            with Image.open(original_image_path) as img:
                img.save(new_image_path, format='PNG')
                print(f"Converted {original_image_path} to {new_image_path}")
                return new_image_path

        except Exception as e:
            raise Exception(f"Error in pdf_to_png_converter: {str(e)}")


class OldImagesCleaner(View):
    def get(self,request):
        images=UplodedImage.objects.all()
        current=time.time()
        for img in images:            
            upload_time=img.uploaded_at.timestamp()
            print(img.uploaded_at)
            if (current-upload_time)>=3600:

                if img.image and os.path.exists(img.image.path):
                    os.remove(img.image.path)
                
                if img.compressed_image and os.path.exists(img.compressed_image.path):
                    os.remove(img.compressed_image.path)
                
                if img.converted_image and os.path.exists(img.converted_image.path):
                    os.remove(img.converted_image.path)
                
                if img.resized_image and os.path.exists(img.resized_image.path):
                    os.remove(img.resized_image.path)
                
                img.delete()
                
        return HttpResponse("done")




class ImageEnhancerView(View):
    def get(self, request):
        return render(request, "imageenhancer.html")

    def post(self, request):
        img = request.FILES.get('image')
        if not img:
            return HttpResponse("No image uploaded.", status=400)

        # Open the uploaded image
        try:
            original_image = Image.open(img)
        except Exception as e:
            return HttpResponse(f"Error processing image: {e}", status=400)

        # Convert to RGB if the image is in RGBA or P mode
        if original_image.mode in ("RGBA", "P"):
            original_image = original_image.convert("RGB")

        # increase brightness and sharpness)
        enhancer = ImageEnhance.Brightness(original_image)
        enhanced_image = enhancer.enhance(1.5)  # Brightness factor (1.0 = original)

        enhancer = ImageEnhance.Sharpness(enhanced_image)
        enhanced_image = enhancer.enhance(2.0)  # Sharpness factor

        # Convert images to base64 to render in the template
        def image_to_base64(image):
            buffer = io.BytesIO()
            image_format = image.format or 'JPEG'
            image.save(buffer, format=image_format)
            buffer.seek(0)
            return base64.b64encode(buffer.getvalue()).decode()

        original_image_base64 = image_to_base64(original_image)
        enhanced_image_base64 = image_to_base64(enhanced_image)

        # Save enhanced image to a BytesIO buffer for download
        buffer = io.BytesIO()
        enhanced_image.save(buffer, format=original_image.format or 'JPEG')
        buffer.seek(0)

        print("done")
        return render(request, "enhanced_sucess.html", {
            'original_image': original_image_base64,
            'enhanced_image': enhanced_image_base64,
            'download_file': buffer.getvalue(),
            'image_format': (original_image.format or 'JPEG').lower()
        })




    




   
        




