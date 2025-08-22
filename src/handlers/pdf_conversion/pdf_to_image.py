import os
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from pdf2image import convert_from_path
from PIL import Image
import asyncio
import time

async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("🚀 [DEBUG] Iniciando handle_pdf...")
    start_time = time.time()
    
    try:
        print("📡 [DEBUG] Enviando chat action...")
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.UPLOAD_PHOTO
        )
        print("✅ [DEBUG] Chat action enviado correctamente")
    except Exception as e:
        print(f"❌ [DEBUG] Error enviando chat action: {e}")
    
    try:
        print("💬 [DEBUG] Enviando mensaje de procesamiento...")
        processing_msg = await update.message.reply_text("⏳ Procesando tu PDF, puede tardar un poco...")
        print("✅ [DEBUG] Mensaje de procesamiento enviado")
    except Exception as e:
        print(f"❌ [DEBUG] Error enviando mensaje: {e}")
        processing_msg = None

    print("📄 [DEBUG] Obteniendo información del archivo...")
    file_info = update.message.document
    print(f"📊 [DEBUG] Archivo: {file_info.file_name}, Tamaño: {file_info.file_size} bytes")
    
    try:
        print("⬇️ [DEBUG] Obteniendo file object...")
        file = await update.message.document.get_file()
        print("✅ [DEBUG] File object obtenido correctamente")
    except Exception as e:
        print(f"❌ [DEBUG] Error obteniendo file object: {e}")
        if processing_msg:
            await processing_msg.edit_text(f"❌ Error obteniendo archivo: {str(e)}")
        return

    temp_dir = os.getenv("TEMP_DIR", "./temp")
    pdf_path = os.path.join(temp_dir, f"input_{update.effective_chat.id}_{int(time.time())}.pdf")
    print(f"📂 [DEBUG] Directorio temporal: {temp_dir}")
    print(f"📄 [DEBUG] Ruta PDF: {pdf_path}")

    try:
        print("⬇️ [DEBUG] Iniciando descarga del archivo...")
        download_start = time.time()
        await file.download_to_drive(pdf_path)
        download_time = time.time() - download_start
        print(f"✅ [DEBUG] Archivo descargado en {download_time:.2f} segundos")
        
        # Verificar que el archivo existe y tiene contenido
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"✅ [DEBUG] Archivo guardado correctamente: {file_size} bytes")
        else:
            print("❌ [DEBUG] Archivo no se guardó correctamente")
            return

        print("🔄 [DEBUG] Iniciando procesamiento por lotes...")
        
        # Procesar en lotes de 3 páginas para evitar timeout
        page_count = 0
        batch_size = 3
        batch_number = 1
        
        while True:
            start_page = page_count + 1
            end_page = page_count + batch_size
            
            print(f"📦 [DEBUG] === LOTE {batch_number} ===")
            print(f"📄 [DEBUG] Procesando páginas {start_page} a {end_page}")
            batch_start = time.time()
            
            try:
                print("🖼️ [DEBUG] Llamando a convert_from_path...")
                convert_start = time.time()
                
                # Procesar solo un lote
                images = convert_from_path(
                    pdf_path, 
                    dpi=500, 
                    first_page=start_page, 
                    last_page=end_page
                )
                
                convert_time = time.time() - convert_start
                print(f"✅ [DEBUG] convert_from_path completado en {convert_time:.2f}s")
                print(f"📊 [DEBUG] Obtenidas {len(images) if images else 0} imágenes")
                
                if not images:  # No hay más páginas
                    print("🏁 [DEBUG] No hay más imágenes, terminando...")
                    break
                
                print(f"🖼️ [DEBUG] Procesando {len(images)} imágenes del lote...")
                
                for i, img in enumerate(images):
                    page_num = start_page + i
                    print(f"📄 [DEBUG] Procesando página {page_num}...")
                    
                    # Redimensionar
                    original_size = img.size
                    img.thumbnail((2048, 2048), Image.LANCZOS)
                    new_size = img.size
                    print(f"📏 [DEBUG] Página {page_num}: {original_size} -> {new_size}")
                    
                    # Guardar
                    reduced_path = os.path.join(temp_dir, f"page_{page_num}_{update.effective_chat.id}.jpg")
                    print(f"💾 [DEBUG] Guardando en: {reduced_path}")
                    
                    save_start = time.time()
                    img.save(reduced_path, "JPEG", quality=95, optimize=True)
                    save_time = time.time() - save_start
                    print(f"✅ [DEBUG] Imagen guardada en {save_time:.2f}s")
                    
                    # Verificar tamaño del archivo guardado
                    if os.path.exists(reduced_path):
                        saved_size = os.path.getsize(reduced_path)
                        print(f"📊 [DEBUG] Tamaño archivo guardado: {saved_size} bytes")
                    
                    # Enviar
                    try:
                        print(f"📤 [DEBUG] Enviando página {page_num}...")
                        send_start = time.time()
                        
                        with open(reduced_path, "rb") as f:
                            await update.message.reply_photo(f, caption=f"Página {page_num}")
                        
                        send_time = time.time() - send_start
                        print(f"✅ [DEBUG] Página {page_num} enviada en {send_time:.2f}s")
                        
                    except Exception as send_error:
                        print(f"❌ [DEBUG] Error enviando página {page_num}: {send_error}")
                    
                    # Limpiar
                    try:
                        os.remove(reduced_path)
                        print(f"🗑️ [DEBUG] Archivo temporal página {page_num} eliminado")
                    except Exception as remove_error:
                        print(f"⚠️ [DEBUG] Error eliminando archivo temporal: {remove_error}")
                
                page_count += len(images)
                batch_time = time.time() - batch_start
                print(f"✅ [DEBUG] Lote {batch_number} completado en {batch_time:.2f}s")
                print(f"📊 [DEBUG] Total páginas procesadas hasta ahora: {page_count}")
                
                # Si se procesan menos páginas que el batch_size, se termina
                if len(images) < batch_size:
                    print("🏁 [DEBUG] Último lote procesado, terminando...")
                    break
                    
                # Pausa entre lotes para evitar timeout
                print("⏳ [DEBUG] Pausa de 1 segundo entre lotes...")
                await asyncio.sleep(1)
                batch_number += 1
                
            except Exception as batch_error:
                print(f"❌ [DEBUG] Error en lote {batch_number}: {batch_error}")
                print("🔄 [DEBUG] Cambiando a procesamiento página por página...")
                
                for page_num in range(start_page, end_page + 1):
                    try:
                        print(f"📄 [DEBUG] Procesando página individual {page_num}...")
                        
                        single_image = convert_from_path(
                            pdf_path, 
                            dpi=500, 
                            first_page=page_num, 
                            last_page=page_num
                        )
                        
                        if not single_image:
                            print(f"❌ [DEBUG] No se pudo obtener página {page_num}")
                            break
                            
                        img = single_image[0]
                        img.thumbnail((2048, 2048), Image.LANCZOS)
                        
                        reduced_path = os.path.join(temp_dir, f"page_{page_num}_{update.effective_chat.id}.jpg")
                        img.save(reduced_path, "JPEG", quality=95, optimize=True)
                        
                        with open(reduced_path, "rb") as f:
                            await update.message.reply_photo(f, caption=f"Página {page_num}")
                        
                        os.remove(reduced_path)
                        page_count += 1
                        print(f"✅ [DEBUG] Página individual {page_num} procesada correctamente")
                        
                    except Exception as single_error:
                        print(f"❌ [DEBUG] Error procesando página individual {page_num}: {single_error}")
                        break
                
                print("🛑 [DEBUG] Terminando después de procesamiento individual")
                break

        total_time = time.time() - start_time
        print(f"🏁 [DEBUG] Procesamiento completado!")
        print(f"📊 [DEBUG] Total de páginas procesadas: {page_count}")
        print(f"⏱️ [DEBUG] Tiempo total: {total_time:.2f} segundos")
        
        if processing_msg:
            try:
                await processing_msg.edit_text(f"✅ PDF procesado correctamente! {page_count} páginas convertidas en {total_time:.1f}s")
            except:
                print("⚠️ [DEBUG] No se pudo editar mensaje de procesamiento")

    except Exception as e:
        total_time = time.time() - start_time
        print(f"❌ [DEBUG] Error general después de {total_time:.2f}s: {e}")
        print(f"❌ [DEBUG] Tipo de error: {type(e).__name__}")
        import traceback
        print(f"❌ [DEBUG] Traceback completo:")
        traceback.print_exc()
        
        if processing_msg:
            try:
                await processing_msg.edit_text(f"❌ Error al procesar el PDF: {str(e)}")
            except:
                print("⚠️ [DEBUG] No se pudo editar mensaje de error")
                
    finally:
        print("🧹 [DEBUG] Iniciando limpieza final...")
        if os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
                print("✅ [DEBUG] Archivo PDF principal eliminado")
            except Exception as cleanup_error:
                print(f"⚠️ [DEBUG] Error eliminando PDF principal: {cleanup_error}")
        else:
            print("ℹ️ [DEBUG] Archivo PDF principal no existe para eliminar")
        
        total_execution_time = time.time() - start_time
        print(f"🏁 [DEBUG] handle_pdf terminado después de {total_execution_time:.2f} segundos")