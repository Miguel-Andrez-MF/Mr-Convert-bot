from PIL import Image
import os

def convert_image(input_path, output_format):
    """
    Convierte una imagen a otro formato.
    input_path: ruta de la imagen original
    output_format: 'JPEG' o 'PNG'
    """
    img = Image.open(input_path)
    
    if output_format == "JPEG":
        img = img.convert("RGB")
    
    # nuevo nombre de archivo
    base_name = os.path.splitext(input_path)[0]
    output_path = f"{base_name}.{output_format.lower()}"
    
    img.save(output_path, output_format)
    return output_path


