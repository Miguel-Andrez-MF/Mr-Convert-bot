from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "convert_image":
        context.user_data["mode"] = "image"
        await query.edit_message_text("📸 Envía una imagen (PNG o JPG) para convertir.")
    elif query.data == "convert_pdf":
        context.user_data["mode"] = "pdf"
        await query.edit_message_text("📄 Envía un archivo PDF para convertir.")


async def show_continue_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🖼 Convertir Imagen (PNG ↔ JPG)", callback_data="convert_image")],
        [InlineKeyboardButton("📄 PDF a Imágenes", callback_data="convert_pdf")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("¿Quieres hacer algo más?", reply_markup=reply_markup)
    else:
        await update.callback_query.message.reply_text("¿Quieres hacer algo más?", reply_markup=reply_markup)


def with_continue_menu(func):
    async def wrapper(update, context):
        await func(update, context)
        await show_continue_menu(update, context)
    return wrapper
