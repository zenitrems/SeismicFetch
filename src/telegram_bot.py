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
from helpers import logger

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


# logging.getLogger("httpx").setLevel(logging.WARNING)
handler = logging.handlers.SysLogHandler(address=("localhost", 514))
logger.add(handler)


class MyBot:
    """Bot class"""

    def __init__(self):
        self.token = os.getenv("TELEGRAM_KEY")
        self.bot = Bot(token=self.token)
        self.app = (
            ApplicationBuilder().connection_pool_size(3).token(self.token).build()
        )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/start command method"""
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Soy un robotsin"
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle message from chat"""
        message_text = update.message.text
        print(update.effective_chat.id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=message_text
        )

    async def send_evento(self, evento):
        """send evento to chat"""
        async with self.bot as bot:
            try:
                await bot.send_message(
                    chat_id="@earthquake_notify", text=evento, parse_mode="HTML"
                )
            except TelegramError as telegram_error:
                logging.error(telegram_error)

            logger.info("Send")

    async def send_error(self, evento):
        """send error to bot chat"""
        async with self.bot as bot:
            try:
                texto = f"<b>ERROR</b>\n\n</code>{evento}</code>"
                await bot.send_message(
                    chat_id=os.getenv("TELEGRAM_CHAT_ID"), text=texto, parse_mode="HTML"
                )
            except TelegramError as telegram_error:
                logger.error(telegram_error)
            logger.info("Telegram Notify")

    def main(self):
        """run method"""
        start_handler = CommandHandler("start", self.start)
        self.app.add_handler(start_handler)
        message_handler = MessageHandler(None, self.handle_message)
        self.app.add_handler(message_handler)

        self.app.run_polling()


# Start Bot Script
if __name__ == "__main__":
    start = MyBot()
    asyncio.run(start.main())
