import os
import uuid
from telegram import Update
from telegram.ext import ContextTypes
from src.utils.image_tools import convert_image
from dotenv import load_dotenv

load_dotenv()
TEMP_DIR = os.getenv("TEMP_DIR", "./temp")

def temp_filename(ext: str) -> str:
    return os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}{ext}")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        ext = ".jpg"
    elif update.message.document:
        file = await update.message.document.get_file()
        ext = os.path.splitext(update.message.document.file_name)[1]
    else:
        await update.message.reply_text("No reconozco el tipo de archivo.")
        return

    input_path = temp_filename(ext)
    await file.download_to_drive(input_path)

    
    output_format = "PNG" if ext.lower() in [".jpg", ".jpeg"] else "JPEG"

    output_path = convert_image(input_path, output_format)

    await update.message.reply_document(open(output_path, "rb"))

    os.remove(input_path)
    os.remove(output_path)
