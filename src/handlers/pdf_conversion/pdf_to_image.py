import os
import psutil
import asyncio
import time
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from pdf2image import convert_from_path
from PIL import Image

async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convertidor PDF adaptativo - Calidad alta para archivos pequeños, optimizado para grandes"""
    print("🚀 [DEBUG] Iniciando handle_pdf adaptativo...")
    start_time = time.time()
    
    try:
        # Verificar información del archivo
        file_info = update.message.document
        file_size_mb = file_info.file_size / (1024 * 1024)
        print(f"📊 [DEBUG] Archivo: {file_info.file_name}, Tamaño: {file_size_mb:.2f}MB")
        
        # Determinar el modo de procesamiento basado en el tamaño
        if file_size_mb < 2.0:
            print("🎨 [MODE] ALTA CALIDAD - Archivo pequeño")
            await handle_pdf_high_quality(update, context, file_info, file_size_mb, start_time)
        else:
            print("⚡ [MODE] OPTIMIZADO - Archivo grande")
            await handle_pdf_optimized(update, context, file_info, file_size_mb, start_time)
            
    except Exception as e:
        print(f"❌ [DEBUG] Error en handle_pdf: {e}")
        await update.message.reply_text(f"❌ Error procesando PDF: {str(e)}")

# =============================================================================
# MODO ALTA CALIDAD - Para archivos < 2MB
# =============================================================================
async def handle_pdf_high_quality(update: Update, context: ContextTypes.DEFAULT_TYPE, file_info, file_size_mb, start_time):
    """Procesamiento de alta calidad para archivos pequeños (< 2MB)"""
    
    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.UPLOAD_PHOTO
        )
        
        processing_msg = await update.message.reply_text(
            f"⏳ **Procesando PDF en ALTA CALIDAD**\n\n"
            f"📄 {file_info.file_name} ({file_size_mb:.1f}MB)\n"
            f"🎨 DPI: 500 - Máxima resolución\n\n"
            f"*Procesando...*"
        )
        
        # Descargar archivo
        file = await update.message.document.get_file()
        temp_dir = os.getenv("TEMP_DIR", "./temp")
        pdf_path = os.path.join(temp_dir, f"input_{update.effective_chat.id}_{int(time.time())}.pdf")
        
        await file.download_to_drive(pdf_path)
        print("✅ [DEBUG] Archivo descargado para procesamiento de alta calidad")
        
        # Procesamiento en lotes de 3 páginas (como el código original)
        page_count = 0
        batch_size = 3
        batch_number = 1
        
        while True:
            start_page = page_count + 1
            end_page = page_count + batch_size
            
            print(f"📦 [DEBUG] === LOTE {batch_number} (ALTA CALIDAD) ===")
            print(f"📄 [DEBUG] Procesando páginas {start_page} a {end_page}")
            
            try:
                # DPI alta calidad para archivos pequeños
                images = convert_from_path(
                    pdf_path, 
                    dpi=500,  # DPI ORIGINAL ALTA CALIDAD
                    first_page=start_page, 
                    last_page=end_page
                )
                
                if not images:  # No hay más páginas
                    print("🏁 [DEBUG] No hay más imágenes, terminando...")
                    break
                
                print(f"🖼️ [DEBUG] Procesando {len(images)} imágenes del lote (alta calidad)...")
                
                for i, img in enumerate(images):
                    page_num = start_page + i
                    print(f"📄 [DEBUG] Procesando página {page_num} (alta calidad)...")
                    
                    # Redimensionar conservando alta calidad
                    original_size = img.size
                    img.thumbnail((2048, 2048), Image.LANCZOS)  # Tamaño original
                    new_size = img.size
                    print(f"📏 [DEBUG] Página {page_num}: {original_size} -> {new_size}")
                    
                    # Guardar con alta calidad
                    reduced_path = os.path.join(temp_dir, f"page_{page_num}_{update.effective_chat.id}.jpg")
                    img.save(reduced_path, "JPEG", quality=95, optimize=True)  # Calidad original
                    
                    # Enviar
                    try:
                        with open(reduced_path, "rb") as f:
                            await update.message.reply_photo(f, caption=f"📄 Página {page_num} (Alta Calidad)")
                        print(f"✅ [DEBUG] Página {page_num} enviada en alta calidad")
                    except Exception as send_error:
                        print(f"❌ [DEBUG] Error enviando página {page_num}: {send_error}")
                    
                    # Limpiar
                    try:
                        os.remove(reduced_path)
                    except:
                        pass
                
                page_count += len(images)
                
                # Si se procesan menos páginas que el batch_size, se termina
                if len(images) < batch_size:
                    print("🏁 [DEBUG] Último lote procesado, terminando...")
                    break
                    
                # Pausa breve entre lotes
                await asyncio.sleep(1)
                batch_number += 1
                
            except Exception as batch_error:
                print(f"❌ [DEBUG] Error en lote {batch_number}: {batch_error}")
                # Fallback: procesamiento página por página
                for page_num in range(start_page, end_page + 1):
                    try:
                        single_image = convert_from_path(
                            pdf_path, 
                            dpi=500,  # Mantener alta calidad
                            first_page=page_num, 
                            last_page=page_num
                        )
                        
                        if not single_image:
                            break
                            
                        img = single_image[0]
                        img.thumbnail((2048, 2048), Image.LANCZOS)
                        
                        reduced_path = os.path.join(temp_dir, f"page_{page_num}_{update.effective_chat.id}.jpg")
                        img.save(reduced_path, "JPEG", quality=95, optimize=True)
                        
                        with open(reduced_path, "rb") as f:
                            await update.message.reply_photo(f, caption=f"📄 Página {page_num} (Alta Calidad)")
                        
                        os.remove(reduced_path)
                        page_count += 1
                        
                    except Exception as single_error:
                        print(f"❌ [DEBUG] Error procesando página individual {page_num}: {single_error}")
                        break
                
                break
        
        total_time = time.time() - start_time
        
        try:
            await processing_msg.edit_text(
                f"✅ **¡PDF procesado en ALTA CALIDAD!**\n\n"
                f"📄 {file_info.file_name}\n"
                f"📊 Páginas convertidas: {page_count}\n"
                f"🎨 Calidad: DPI 500 - Máxima resolución\n"
                f"⏱️ Tiempo: {total_time:.1f}s"
            )
        except:
            pass
        
    except Exception as e:
        print(f"❌ [DEBUG] Error en modo alta calidad: {e}")
        await update.message.reply_text(f"❌ Error procesando PDF en alta calidad: {str(e)}")
    
    finally:
        # Limpiar archivo PDF
        try:
            if 'pdf_path' in locals() and os.path.exists(pdf_path):
                os.remove(pdf_path)
        except:
            pass

# =============================================================================
# MODO OPTIMIZADO - Para archivos >= 2MB
# =============================================================================
async def handle_pdf_optimized(update: Update, context: ContextTypes.DEFAULT_TYPE, file_info, file_size_mb, start_time):
    """Procesamiento optimizado para archivos grandes (>= 2MB)"""
    
    # Verificar recursos disponibles
    memory = psutil.virtual_memory()
    print(f"📊 [MEMORY] Disponible: {memory.available / 1024**2:.1f}MB, Uso: {memory.percent}%")
    
    # Si la memoria disponible es muy poca, cancelar
    if memory.available < 200 * 1024 * 1024:  # Menos de 200MB
        await update.message.reply_text(
            "❌ **Memoria insuficiente**\n\n"
            "El sistema no tiene suficiente memoria para procesar este archivo. "
            "Intenta con un PDF más pequeño o inténtalo más tarde."
        )
        return
    
    # Limitar tamaño de archivo para modo optimizado
    if file_size_mb > 8:
        await update.message.reply_text(
            f"❌ **Archivo muy grande**\n\n"
            f"📄 Archivo: {file_info.file_name}\n"
            f"📏 Tamaño: {file_size_mb:.2f}MB\n\n"
            f"Por limitaciones del servidor, solo se pueden procesar PDFs de hasta 8MB.\n"
            f"Comprime tu PDF o divídelo en archivos más pequeños."
        )
        return
    
    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.UPLOAD_PHOTO
        )
        
        processing_msg = await update.message.reply_text(
            f"⏳ **Procesando PDF OPTIMIZADO**\n\n"
            f"📄 {file_info.file_name} ({file_size_mb:.1f}MB)\n"
            f"⚡ DPI adaptativo - Optimizado para servidor ligero\n\n"
            f"*Esto puede tomar 1-2 minutos*"
        )
        
        # Descargar archivo
        file = await update.message.document.get_file()
        temp_dir = os.getenv("TEMP_DIR", "./temp")
        pdf_path = os.path.join(temp_dir, f"input_{update.effective_chat.id}_{int(time.time())}.pdf")
        
        await file.download_to_drive(pdf_path)
        print("✅ [DEBUG] Archivo descargado para procesamiento optimizado")
        
        # Configuración adaptativa basada en memoria disponible
        memory_check = psutil.virtual_memory()
        if memory_check.available < 300 * 1024 * 1024:  # Menos de 300MB
            dpi = 300
            max_dimension = 1024
            quality = 80
        elif memory_check.available < 500 * 1024 * 1024:  # Menos de 500MB
            dpi = 400
            max_dimension = 1536
            quality = 90
        else:
            dpi = 450
            max_dimension = 2048
            quality = 85
        
        print(f"🎛️ [CONFIG] DPI: {dpi}, Max dimension: {max_dimension}, Quality: {quality}")
        
        # Procesamiento página por página
        page_count = 0
        consecutive_errors = 0
        batch_number = 1
        
        while consecutive_errors < 3:
            start_page = page_count + 1
            
            try:
                # Actualizar progreso cada 3 páginas
                if batch_number % 3 == 0:
                    try:
                        await processing_msg.edit_text(
                            f"⏳ **Procesando PDF OPTIMIZADO**\n\n"
                            f"📄 {file_info.file_name}\n"
                            f"📊 Procesadas: {page_count} páginas\n"
                            f"🔄 Trabajando en página {start_page}...\n"
                            f"⚡ Modo: DPI {dpi} optimizado"
                        )
                    except:
                        pass
                
                # Verificar memoria antes de cada página
                mem_check = psutil.virtual_memory()
                if mem_check.available < 150 * 1024 * 1024:  # Menos de 150MB
                    print("⚠️ [MEMORY] Memoria baja, limpiando...")
                    import gc
                    gc.collect()
                    await asyncio.sleep(2)
                
                # Convertir una página
                images = convert_from_path(
                    pdf_path,
                    dpi=dpi,
                    first_page=start_page,
                    last_page=start_page,  # Solo una página a la vez
                    thread_count=1
                )
                
                if not images:
                    print(f"🏁 [DEBUG] No hay más páginas después de {page_count}")
                    break
                
                # Procesar imagen con configuración optimizada
                img = images[0]
                original_size = img.size
                
                if img.width > max_dimension or img.height > max_dimension:
                    img.thumbnail((max_dimension, max_dimension), Image.LANCZOS)
                
                new_size = img.size
                print(f"📏 [DEBUG] Página {start_page}: {original_size} -> {new_size}")
                
                # Guardar con configuración optimizada
                reduced_path = os.path.join(temp_dir, f"page_{start_page}_{update.effective_chat.id}.jpg")
                img.save(reduced_path, "JPEG", quality=quality, optimize=True)
                
                # Limpiar memoria inmediatamente
                del img
                del images
                import gc
                gc.collect()
                
                # Enviar imagen
                try:
                    with open(reduced_path, "rb") as f:
                        await update.message.reply_photo(
                            f, 
                            caption=f"📄 Página {start_page} (Optimizado DPI {dpi})"
                        )
                    consecutive_errors = 0
                except Exception as send_error:
                    print(f"❌ [DEBUG] Error enviando página {start_page}: {send_error}")
                    consecutive_errors += 1
                
                # Limpiar archivo temporal
                try:
                    os.remove(reduced_path)
                except:
                    pass
                
                page_count += 1
                batch_number += 1
                
                # Pausa entre páginas para t2.micro
                await asyncio.sleep(1.5)
                
            except Exception as page_error:
                print(f"❌ [DEBUG] Error procesando página {start_page}: {page_error}")
                consecutive_errors += 1
                
                if consecutive_errors >= 3:
                    await processing_msg.edit_text(
                        f"❌ **Error de procesamiento**\n\n"
                        f"Se procesaron {page_count} páginas antes del error.\n"
                        f"Intenta con un archivo más pequeño."
                    )
                    break
                
                await asyncio.sleep(3)
        
        total_time = time.time() - start_time
        
        if page_count > 0:
            try:
                await processing_msg.edit_text(
                    f"✅ **¡PDF procesado en MODO OPTIMIZADO!**\n\n"
                    f"📄 {file_info.file_name}\n"
                    f"📊 Páginas convertidas: {page_count}\n"
                    f"⚡ Configuración: DPI {dpi}, Calidad {quality}%\n"
                    f"⏱️ Tiempo: {total_time:.1f}s\n"
                    f"💡 Optimizado para servidor ligero"
                )
            except:
                pass
        
    except Exception as e:
        print(f"❌ [DEBUG] Error en modo optimizado: {e}")
        await update.message.reply_text(f"❌ Error procesando PDF optimizado: {str(e)}")
    
    finally:
        # Limpieza final
        try:
            if 'pdf_path' in locals() and os.path.exists(pdf_path):
                os.remove(pdf_path)
        except:
            pass
        
        # Forzar limpieza de memoria
        import gc
        gc.collect()