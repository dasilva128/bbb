import asyncio
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
from bot.bot import start, handle_callback, handle_message, cancel, ADD_CUSTOM_TEXT, ADD_CUSTOM_POSITION, ADD_CUSTOM_CONTENT, ADD_SYSTEM_TEXT, ADD_SYSTEM_POSITION, ADD_SYSTEM_CONTENT, SEND_MESSAGE_TO_USER, SEND_MESSAGE_CONTENT
from bot.database import init_db
from dotenv import load_dotenv
import os

# تنظیم لاگ‌گیری
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv('config/config.env')

async def main():
    app = None
    try:
        logger.info("Initializing database...")
        init_db(os.getenv('MONGODB_URI'), os.getenv('MONGODB_DB'))

        logger.info("Building Telegram application...")
        app = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()

        # ConversationHandler
        conv_handler = ConversationHandler(
            entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
            states={
                ADD_CUSTOM_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
                ADD_CUSTOM_POSITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
                ADD_CUSTOM_CONTENT: [MessageHandler(filters.TEXT | filters.AUDIO | filters.VIDEO | filters.Document.ALL | filters.PHOTO | filters.FORWARDED, handle_message)],
                ADD_SYSTEM_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
                ADD_SYSTEM_POSITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
                ADD_SYSTEM_CONTENT: [MessageHandler(filters.TEXT | filters.AUDIO | filters.VIDEO | filters.Document.ALL | filters.PHOTO | filters.FORWARDED, handle_message)],
                SEND_MESSAGE_TO_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
                SEND_MESSAGE_CONTENT: [MessageHandler(filters.ALL, handle_message)],
            },
            fallbacks=[CommandHandler('cancel', cancel), MessageHandler(filters.Regex('↩️لغو'), cancel)],
        )

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(handle_callback))
        app.add_handler(conv_handler)

        logger.info("Bot is starting...")
        await app.initialize()
        await app.start()
        await app.updater.start_polling()

        while True:
            await asyncio.sleep(1)

    except asyncio.CancelledError:
        logger.info("Received exit signal, shutting down...")
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    finally:
        logger.info("Shutting down bot...")
        if app is not None:
            try:
                if app.updater.running:
                    await app.updater.stop()
                await app.stop()
                await app.shutdown()
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Fatal error: {e}")