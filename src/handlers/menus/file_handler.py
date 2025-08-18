from telegram import Update
from telegram.ext import ContextTypes
from .keyboards import *

# Importar tus funciones existentes directamente
from ..image_conversion.convert_images import handle_image
from ..pdf_conversion.convert_pdf import handle_pdf
from .menu_views import *

# =============================================================================
# HANDLER UNIVERSAL DE ARCHIVOS
# =============================================================================

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler que recibe archivos y llama a la función correspondiente"""
    
    # Verificar si hay un modo configurado
    mode = context.user_data.get("mode")
    handler_func = context.user_data.get("handler")
    
    if not mode or not handler_func:
        await update.message.reply_text(
            "❌ Por favor, selecciona primero una operación desde el menú.\n"
            "Usa /start para ver las opciones disponibles."
        )
        return
    
    # Llamar a tu función existente
    await handler_func(update, context)

def with_continue_menu(func):
    """Decorator que añade menú de continuación después de operaciones"""
    async def wrapper(update, context):
        await func(update, context)
        await show_continue_menu(update, context)
    return wrapper