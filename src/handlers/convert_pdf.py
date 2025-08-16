import os
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from pdf2image import convert_from_path
from PIL import Image

async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.UPLOAD_PHOTO
    )
    processing_msg = await update.message.reply_text("⏳ Procesando tu Archivo, dame un momento...")

    
    file = await update.message.document.get_file()
    temp_dir = os.getenv("TEMP_DIR", "./temp")
    pdf_path = os.path.join(temp_dir, "input.pdf")

    await file.download_to_drive(pdf_path)

    images = convert_from_path(pdf_path, dpi=500)

    await processing_msg.delete()

    for i, img in enumerate(images):
        img.thumbnail((2048, 2048), Image.LANCZOS)

        reduced_path = os.path.join(temp_dir, f"page_{i+1}.jpg")
        img.save(reduced_path, "JPEG")

        with open(reduced_path, "rb") as f:
            await update.message.reply_photo(f)

        os.remove(reduced_path)

    os.remove(pdf_path)
