import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from bot.bot import start, handle_callback, handle_message, cancel, ADD_CUSTOM_TEXT, ADD_CUSTOM_POSITION, ADD_CUSTOM_CONTENT, ADD_SYSTEM_TEXT, ADD_SYSTEM_POSITION, ADD_SYSTEM_CONTENT
from bot.database import init_db
from dotenv import load_dotenv
import os

load_dotenv('config/config.env')

async def main():
    init_db(os.getenv('MONGODB_URI'), os.getenv('MONGODB_DB'))

    app = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()

    # ConversationHandler برای دکمه‌های سفارشی و سیستمی
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        states={
            ADD_CUSTOM_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
            ADD_CUSTOM_POSITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
            ADD_CUSTOM_CONTENT: [MessageHandler(filters.TEXT | filters.AUDIO | filters.VIDEO | filters.Document.ALL | filters.PHOTO | filters.FORWARD, handle_message)],
            ADD_SYSTEM_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
            ADD_SYSTEM_POSITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
            ADD_SYSTEM_CONTENT: [MessageHandler(filters.TEXT | filters.AUDIO | filters.VIDEO | filters.Document.ALL | filters.PHOTO | filters.FORWARD, handle_message)],
        },
        fallbacks=[CommandHandler('cancel', cancel), MessageHandler(filters.Regex('↩️لغو'), cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(conv_handler)

    print("Bot is running...")
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())