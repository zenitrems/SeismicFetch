"""
Telegram bot
"""
import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
)
from telegram.error import TelegramError
from src import helpers

load_dotenv()


logger = helpers.logger


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


# logging.getLogger("httpx").setLevel(logging.WARNING)
handler = logging.handlers.SysLogHandler(address=("localhost", 514))
logger.add(handler)


class MyBot:
    """Main Telegram Bot Class"""

    def __init__(self):
        self.token = os.getenv("TELEGRAM_KEY")
        self.bot = Bot(token=self.token)
        self.app = (
            ApplicationBuilder().connection_pool_size(3).token(self.token).build()
        )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle Telegram chat command /start"""
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Soy un robotsin"
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incomming chat messages"""
        message_text = update.message.text
        print(update.effective_chat.id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=message_text
        )

    async def send_update(self, update, location):
        """Send Event to the defined chat_id"""
        async with self.bot as bot:
            try:
                await bot.send_message(
                    chat_id=os.getenv("TELEGRAM_GROUP"), text=update, parse_mode="HTML"
                )
                """ await bot.send_location(
                    chat_id=os.getenv("TELEGRAM_GROUP"),
                    latitude=location[0],
                    longitude=location[1],
                    disable_notification=True,
                ) """
            except TelegramError as telegram_error:
                logging.error(telegram_error)

            logger.info("Send")

    async def send_error(self, error):
        """Send Error updates to the defined chat_id"""
        async with self.bot as bot:
            try:
                error_text = f"<b>ERROR</b>\n\n</code>{error}</code>"
                await bot.send_message(
                    chat_id=os.getenv("TELEGRAM_CHAT_ID"),
                    text=error_text,
                    parse_mode="HTML",
                )
            except TelegramError as telegram_error:
                logger.error(telegram_error)
            logger.info("Telegram Notify")

    def main(self):
        """Main Bot run Method(Standalone)"""
        start_handler = CommandHandler("start", self.start)
        self.app.add_handler(start_handler)
        message_handler = MessageHandler(None, self.handle_message)
        self.app.add_handler(message_handler)

        self.app.run_polling()


# Start Bot Script
if __name__ == "__main__":
    start = MyBot()
    asyncio.run(start.main())
