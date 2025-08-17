import os
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from pdf2image import convert_from_path
from PIL import Image
import asyncio

async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.UPLOAD_PHOTO
    )
    processing_msg = await update.message.reply_text("⏳ Procesando tu PDF, puede tardar un poco...")

    file = await update.message.document.get_file()
    temp_dir = os.getenv("TEMP_DIR", "./temp")
    
    pdf_path = os.path.join(temp_dir, "input.pdf")

    try:
        await file.download_to_drive(pdf_path)

        # Procesar en lotes de 3 páginas para evitar timeout
        page_count = 0
        batch_size = 3
        
        while True:
            start_page = page_count + 1
            end_page = page_count + batch_size
            
            try:
                # Procesar solo un lote
                images = convert_from_path(
                    pdf_path, 
                    dpi=500, 
                    first_page=start_page, 
                    last_page=end_page
                )
                
                if not images:  # No hay más páginas
                    break
                
                for i, img in enumerate(images):
                    img.thumbnail((2048, 2048), Image.LANCZOS)
                    
                    reduced_path = os.path.join(temp_dir, f"page_{start_page + i}.jpg")
                    img.save(reduced_path, "JPEG", quality=95, optimize=True)
                    
                    with open(reduced_path, "rb") as f:
                        await update.message.reply_photo(f)
                    
                    os.remove(reduced_path)
                
                page_count += len(images)
                
                # Si c procesan menos páginas que el batch_size, c termina
                if len(images) < batch_size:
                    break
                    
                # Pausa entre lotes para timeout feo
                await asyncio.sleep(1)
                
            except Exception as batch_error:
                print("Fallo el lote, procesando página por página...")
                for page_num in range(start_page, end_page + 1):
                    try:
                        single_image = convert_from_path(
                            pdf_path, 
                            dpi=500, 
                            first_page=page_num, 
                            last_page=page_num
                        )
                        
                        if not single_image:
                            break
                            
                        img = single_image[0]
                        img.thumbnail((2048, 2048), Image.LANCZOS)
                        
                        reduced_path = os.path.join(temp_dir, f"page_{page_num}.jpg")
                        img.save(reduced_path, "JPEG", quality=95, optimize=True)
                        
                        with open(reduced_path, "rb") as f:
                            await update.message.reply_photo(f)
                        
                        os.remove(reduced_path)
                        page_count += 1
                        
                    except Exception:
                        break
                
                break

    except Exception as e:
        await processing_msg.edit_text(f"❌ Error al procesar el PDF: {str(e)}")
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)