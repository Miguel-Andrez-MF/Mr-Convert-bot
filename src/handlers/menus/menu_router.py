from telegram import Update
from telegram.ext import ContextTypes
from .menu_views import *
from .keyboards import *

from ..image_conversion.convert_images import handle_image
from ..pdf_conversion.pdf_to_image import handle_pdf
from ..pdf_conversion.image_to_pdf import *
# =============================================================================
# ROUTER PRINCIPAL - MANEJA TODOS LOS CALLBACKS
# =============================================================================

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Router principal - maneja todos los callbacks de menús"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    # Menús principales
    if callback_data == "back_to_main":
        await show_main_menu(query)
    elif callback_data == "menu_images":
        await show_images_menu(query)
    elif callback_data == "menu_documents":
        await show_documents_menu(query)
    elif callback_data == "help":
        await show_help_menu(query)
    
    # ========================================
    # MODOS DE IMÁGENES - HANDLERS ESPECÍFICOS
    # ========================================
    elif callback_data == "convert_format":
        context.user_data["mode"] = "convert_format"
        context.user_data["handler"] = handle_image  # Tu función actual
        await query.edit_message_text(CONVERT_FORMAT_MESSAGE, parse_mode="Markdown")
        
    elif callback_data == "resize_image":
        context.user_data["mode"] = "resize_image"
        # context.user_data["handler"] = handle_resize_image  # Nueva función
        context.user_data["handler"] = handle_image  # Temporal hasta que crees la nueva
        await query.edit_message_text(RESIZE_IMAGE_MESSAGE, parse_mode="Markdown")
        
    elif callback_data == "change_quality":
        context.user_data["mode"] = "change_quality"
        # context.user_data["handler"] = handle_change_quality  # Nueva función
        context.user_data["handler"] = handle_image  # Temporal hasta que crees la nueva
        await query.edit_message_text(CHANGE_QUALITY_MESSAGE, parse_mode="Markdown")
        
    elif callback_data == "apply_filters":
        context.user_data["mode"] = "apply_filters"
        # context.user_data["handler"] = handle_apply_filters  # Nueva función
        context.user_data["handler"] = handle_image  # Temporal hasta que crees la nueva
        await query.edit_message_text(APPLY_FILTERS_MESSAGE, parse_mode="Markdown")
    
    # ========================================
    # MODOS DE DOCUMENTOS - HANDLERS ESPECÍFICOS
    # ========================================
    elif callback_data == "pdf_to_images":
        context.user_data["mode"] = "pdf_to_images"
        context.user_data["handler"] = handle_pdf  # Tu función actual
        await query.edit_message_text(PDF_TO_IMAGES_MESSAGE, parse_mode="Markdown")
        
    elif callback_data == "images_to_pdf":
        context.user_data["mode"] = "images_to_pdf"
        # context.user_data["handler"] = handle_images_to_pdf  # Nueva función
        context.user_data["handler"] = handle_images_to_pdf  # Temporal hasta que crees la nueva
        await query.edit_message_text(IMAGES_TO_PDF_MESSAGE, parse_mode="Markdown")
        
    elif callback_data == "compress_pdf":
        context.user_data["mode"] = "compress_pdf"
        # context.user_data["handler"] = handle_compress_pdf  # Nueva función  
        context.user_data["handler"] = handle_pdf  # Temporal hasta que crees la nueva
        await query.edit_message_text(COMPRESS_PDF_MESSAGE, parse_mode="Markdown")
    
    # Repetir operación
    elif callback_data == "repeat_operation":
        await repeat_operation(query, context)