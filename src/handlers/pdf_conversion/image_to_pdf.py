import os
import uuid
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
TEMP_DIR = os.getenv("TEMP_DIR", "./temp")

def temp_filename(ext: str) -> str:
    return os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}{ext}")

async def handle_images_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la conversión de imágenes a PDF"""
    
    # Inicializar el almacén de imágenes si no existe
    if "pdf_images" not in context.user_data:
        context.user_data["pdf_images"] = []
        context.user_data["pdf_session_id"] = str(int(time.time()))
    
    try:
        # Determinar si es una foto o documento
        if update.message.photo:
            file = await update.message.photo[-1].get_file()
            ext = ".jpg"
            file_name = f"image_{len(context.user_data['pdf_images']) + 1}.jpg"
        elif update.message.document:
            file = await update.message.document.get_file()
            ext = os.path.splitext(update.message.document.file_name)[1].lower()
            file_name = update.message.document.file_name
            
            # Verificar que sea una imagen
            if ext not in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
                await update.message.reply_text(
                    "❌ Solo se aceptan archivos de imagen para convertir a PDF.\n"
                    "Formatos soportados: JPG, PNG, BMP, TIFF, WEBP"
                )
                return
        else:
            await update.message.reply_text("❌ No se reconoce el tipo de archivo.")
            return

        # Descargar la imagen
        session_id = context.user_data["pdf_session_id"]
        input_path = os.path.join(TEMP_DIR, f"pdf_{session_id}_{len(context.user_data['pdf_images'])}{ext}")
        
        await update.message.reply_text("⏳ Procesando imagen...")
        await file.download_to_drive(input_path)
        
        # Procesar la imagen usando la función de utils
        try:
            from src.utils.image_tools import convert_image
            
            # Convertir a JPEG con configuración optimizada para PDF
            processed_path = convert_image(
                input_path=input_path,
                output_format="JPEG",
                quality=95,
                max_size=(2048, 2048)
            )
            
            # Eliminar archivo original si es diferente al procesado
            if input_path != processed_path and os.path.exists(input_path):
                os.remove(input_path)
            
            # Agregar a la lista
            context.user_data["pdf_images"].append(processed_path)
            
        except Exception as img_error:
            print(f"❌ Error procesando imagen: {img_error}")
            await update.message.reply_text(f"❌ Error al procesar la imagen: {str(img_error)}")
            if os.path.exists(input_path):
                os.remove(input_path)
            return
        
        # Mostrar estado actual y opciones
        image_count = len(context.user_data["pdf_images"])
        
        # Teclado con opciones
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📄 Generar PDF", callback_data=f"generate_pdf_{session_id}")],
            [InlineKeyboardButton("🖼️ Agregar más imágenes", callback_data=f"add_more_images_{session_id}")],
            [InlineKeyboardButton("❌ Cancelar", callback_data=f"cancel_pdf_{session_id}")]
        ])
        
        await update.message.reply_text(
            f"✅ **Imagen agregada correctamente**\n\n"
            f"📊 **Estado actual:**\n"
            f"• Imágenes en cola: **{image_count}**\n"
            f"• Archivo: `{file_name}`\n\n"
            f"¿Qué deseas hacer?",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        print(f"❌ Error general en handle_images_to_pdf: {e}")
        await update.message.reply_text(f"❌ Error al procesar: {str(e)}")

async def generate_pdf_from_images(update: Update, context: ContextTypes.DEFAULT_TYPE, session_id: str):
    """Genera el PDF con todas las imágenes recolectadas"""
    
    query = update.callback_query
    await query.answer()
    
    if "pdf_images" not in context.user_data or not context.user_data["pdf_images"]:
        await query.edit_message_text("❌ No hay imágenes para procesar.")
        return
    
    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.UPLOAD_DOCUMENT
        )
        
        processing_msg = await query.edit_message_text("⏳ Generando PDF, por favor espera...")
        
        image_paths = context.user_data["pdf_images"]
        image_count = len(image_paths)
        
        # Cargar todas las imágenes (ya están en formato JPEG desde convert_image)
        images = []
        for i, path in enumerate(image_paths):
            try:
                if os.path.exists(path):
                    img = Image.open(path)
                    images.append(img)
                else:
                    print(f"⚠️ Imagen no encontrada: {path}")
            except Exception as img_error:
                print(f"❌ Error cargando imagen {i}: {img_error}")
        
        if not images:
            await processing_msg.edit_text("❌ No se pudieron cargar las imágenes.")
            return
        
        # Crear el PDF
        pdf_path = os.path.join(TEMP_DIR, f"images_to_pdf_{session_id}.pdf")
        
        if len(images) == 1:
            # Una sola imagen
            images[0].save(pdf_path, "PDF", quality=95, optimize=True)
        else:
            # Múltiples imágenes
            first_image = images[0]
            other_images = images[1:]
            first_image.save(
                pdf_path, 
                "PDF", 
                save_all=True, 
                append_images=other_images,
                quality=95, 
                optimize=True
            )
        
        # Verificar el tamaño del archivo
        pdf_size = os.path.getsize(pdf_path)
        pdf_size_mb = pdf_size / (1024 * 1024)
        
        # Enviar el PDF
        with open(pdf_path, "rb") as pdf_file:
            await update.effective_chat.send_document(
                document=pdf_file,
                filename=f"converted_images_{int(time.time())}.pdf",
                caption=f"✅ **PDF generado exitosamente**\n\n"
                       f"📄 **Detalles:**\n"
                       f"• Páginas: {image_count}\n"
                       f"• Tamaño: {pdf_size_mb:.2f} MB",
                parse_mode="Markdown"
            )
        
        await processing_msg.edit_text(
            f"✅ **¡PDF creado exitosamente!**\n\n"
            f"📊 **Resultado:**\n"
            f"• {image_count} imágenes convertidas\n"
            f"• Tamaño final: {pdf_size_mb:.2f} MB"
        )
        
    except Exception as e:
        print(f"❌ Error generando PDF: {e}")
        await query.edit_message_text(f"❌ Error al generar PDF: {str(e)}")
    
    finally:
        # Limpiar archivos temporales
        cleanup_pdf_session(context, session_id)

def cleanup_pdf_session(context: ContextTypes.DEFAULT_TYPE, session_id: str):
    """Limpia todos los archivos temporales de la sesión PDF"""
    
    if "pdf_images" in context.user_data:
        # Eliminar archivos de imágenes
        for image_path in context.user_data["pdf_images"]:
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"🗑️ Imagen temporal eliminada: {image_path}")
            except Exception as e:
                print(f"⚠️ Error eliminando imagen temporal: {e}")
        
        # Limpiar datos de usuario
        context.user_data.pop("pdf_images", None)
        context.user_data.pop("pdf_session_id", None)
    
    # Eliminar PDF temporal si existe
    pdf_path = os.path.join(TEMP_DIR, f"images_to_pdf_{session_id}.pdf")
    try:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            print(f"🗑️ PDF temporal eliminado: {pdf_path}")
    except Exception as e:
        print(f"⚠️ Error eliminando PDF temporal: {e}")

async def cancel_pdf_session(update: Update, context: ContextTypes.DEFAULT_TYPE, session_id: str):
    """Cancela la sesión actual de creación de PDF"""
    
    query = update.callback_query
    await query.answer()
    
    # Contar imágenes antes de limpiar
    image_count = len(context.user_data.get("pdf_images", []))
    
    # Limpiar sesión
    cleanup_pdf_session(context, session_id)
    
    await query.edit_message_text(
        f"❌ **Sesión cancelada**\n\n"
        f"Se eliminaron {image_count} imágenes en cola.\n"
        f"Puedes empezar una nueva conversión cuando quieras."
    )

async def add_more_images(update: Update, context: ContextTypes.DEFAULT_TYPE, session_id: str):
    """Permite agregar más imágenes a la sesión actual"""
    
    query = update.callback_query
    await query.answer()
    
    image_count = len(context.user_data.get("pdf_images", []))
    
    await query.edit_message_text(
        f"📸 **Continuar agregando imágenes**\n\n"
        f"📊 **Estado actual:** {image_count} imágenes en cola\n\n"
        f"Envía más imágenes y te daré opciones nuevamente."
    )