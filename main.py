import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler

# Importar handlers
from src.handlers.menus.start_handler import start
from src.handlers.menus.menu_router import *
from src.handlers.menus.file_handler import *

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
TEMP_DIR = os.getenv("TEMP_DIR", "./temp")
os.makedirs(TEMP_DIR, exist_ok=True)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CallbackQueryHandler(menu_handler))

    app.add_handler(MessageHandler(
        (filters.PHOTO | filters.Document.ALL) & ~filters.COMMAND,
        with_continue_menu(handle_file)
    ))

    print("🤖 Bot Mr.Convert iniciado...")

    app.run_polling()

if __name__ == "__main__":
    main()