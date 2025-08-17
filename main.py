import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from handlers.menus.start_handler import start
from handlers.menus.menu_handler import menu_handler, with_continue_menu
from handlers.image_conversion.convert_images import handle_image
from handlers.pdf_conversion.convert_pdf import handle_pdf

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
TEMP_DIR = os.getenv("TEMP_DIR", "./temp")
os.makedirs(TEMP_DIR, exist_ok=True)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CallbackQueryHandler(menu_handler))

    app.add_handler(MessageHandler(
        (filters.PHOTO | filters.Document.IMAGE),
        with_continue_menu(handle_image)
    ))
    app.add_handler(MessageHandler(
        filters.Document.PDF,
        with_continue_menu(handle_pdf)
    ))

    print("Bot maquinando🤖...")
    app.run_polling()

if __name__ == "__main__":
    main()
