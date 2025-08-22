from PIL import Image
import os

def convert_image(input_path, output_format, quality=95, max_size=None):
    """
    Convierte una imagen a otro formato.
    input_path: ruta de la imagen original
    output_format: 'JPEG' o 'PNG'
    quality: calidad de compresión (1-100) para JPEG
    max_size: tupla (width, height) para redimensionar manteniendo aspect ratio
    """
    img = Image.open(input_path)
    
    # Redimensionar si se especifica max_size
    if max_size and (img.size[0] > max_size[0] or img.size[1] > max_size[1]):
        img.thumbnail(max_size, Image.LANCZOS)
    
    if output_format == "JPEG":
        # Para JPEG, manejar transparencia con fondo blanco
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                background.paste(img, mask=img.split()[-1])
            img = background
        elif img.mode != 'RGB':
            img = img.convert("RGB")
    
    # nuevo nombre de archivo
    base_name = os.path.splitext(input_path)[0]
    output_path = f"{base_name}.{output_format.lower()}"
    
    # Guardar con parámetros optimizados
    if output_format == "JPEG":
        img.save(output_path, output_format, quality=quality, optimize=True)
    else:
        img.save(output_path, output_format, optimize=True)
    
    return output_path