import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from bot.bot import start, handle_callback, handle_message
from bot.database import init_db
from dotenv import load_dotenv
import os

load_dotenv('config/config.env')

async def main():
    # اتصال به MongoDB
    init_db(os.getenv('MONGODB_URI'), os.getenv('MONGODB_DB'))

    # راه‌اندازی بات
    app = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()

    # هندلرها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # شروع بات
    print("Bot is running...")
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())