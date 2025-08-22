from telegram import Update
from telegram.ext import ContextTypes
from .keyboards import *

# Importar tus funciones existentes directamente
from ..image_conversion.convert_images import handle_image
from ..pdf_conversion.pdf_to_image import handle_pdf

# =============================================================================
# FUNCIONES PARA MOSTRAR MENÚS
# =============================================================================

async def show_main_menu(query):
    """Muestra el menú principal"""
    await query.edit_message_text(
        WELCOME_MESSAGE, 
        reply_markup=MAIN_MENU_KEYBOARD, 
        parse_mode="Markdown"
    )

async def show_images_menu(query):
    """Muestra el menú de imágenes"""
    await query.edit_message_text(
        IMAGES_MENU_MESSAGE, 
        reply_markup=IMAGES_MENU_KEYBOARD, 
        parse_mode="Markdown"
    )

async def show_documents_menu(query):
    """Muestra el menú de documentos"""
    await query.edit_message_text(
        DOCUMENTS_MENU_MESSAGE, 
        reply_markup=DOCUMENTS_MENU_KEYBOARD, 
        parse_mode="Markdown"
    )

async def show_help_menu(query):
    """Muestra el menú de ayuda"""
    await query.edit_message_text(
        HELP_MESSAGE, 
        reply_markup=HELP_MENU_KEYBOARD, 
        parse_mode="Markdown"
    )

# =============================================================================
# MENÚ DE REPETICIÓN DE OPERACIONES
# =============================================================================

async def repeat_operation(query, context):
    """Repite la operación actual"""
    current_mode = context.user_data.get("mode")
    
    if not current_mode:
        await show_main_menu(query)
        return
    
    await query.edit_message_text(
        "🔄 **Repetir operación**\n\n"
        "📎 Envía tu archivo para procesar nuevamente.",
        parse_mode="Markdown"
    )

# =============================================================================
# MENÚ DE CONTINUACIÓN
# =============================================================================

async def show_continue_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el menú de continuación después de procesar archivos"""
    if update.message:
        await update.message.reply_text(
            SUCCESS_MESSAGE, 
            reply_markup=CONTINUE_MENU_KEYBOARD, 
            parse_mode="Markdown"
        )
    else:
        await update.callback_query.message.reply_text(
            SUCCESS_MESSAGE, 
            reply_markup=CONTINUE_MENU_KEYBOARD, 
            parse_mode="Markdown"
        )