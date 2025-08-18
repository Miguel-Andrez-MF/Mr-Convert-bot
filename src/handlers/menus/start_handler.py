from telegram import Update
from telegram.ext import ContextTypes
from .keyboards import MAIN_MENU_KEYBOARD, WELCOME_MESSAGE

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Menú principal de bienvenida"""
    
    context.user_data.clear()
    
    await update.message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=MAIN_MENU_KEYBOARD,
        parse_mode="Markdown"
    )