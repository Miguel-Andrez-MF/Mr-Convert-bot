from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🖼 Convertir Imagen (PNG ↔ JPG)", callback_data="convert_image")],
        [InlineKeyboardButton("📄 PDF a Imágenes", callback_data="convert_pdf")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 ¡Hola! Soy Mr.Convert.\n\nElige qué quieres hacer:",
        reply_markup=reply_markup
    )


    