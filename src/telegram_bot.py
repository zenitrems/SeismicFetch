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

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class MyBot:
    """Bot class"""

    def __init__(self, token):
        self.token = token
        self.bot = Bot(token=self.token)
        self.app = ApplicationBuilder().token(token).build()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/start command method"""
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Soy un robotsin"
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle message from chat"""
        message_text = update.message.text
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)

    async def send_evento(self, evento):
        """send evento to chat"""
        try:
            await self.bot.send_message(
                chat_id="@earthquake_notify", text=evento, parse_mode="HTML"
            )
        except TelegramError as telegram_error:
            logging.exception(telegram_error)

    async def send_error(self, evento):
        """send error to bot chat"""
        try:
            texto = f"<b>ERROR</b>\n\n</code>{evento}</code>"
            await self.bot.send_message(chat_id="1505812784", text=texto, parse_mode="HTML")
        except TelegramError as telegram_error:
            logging.exception(telegram_error)

    def run(self):
        """run method"""
        start_handler = CommandHandler("start", self.start)
        self.app.add_handler(start_handler)

        message_handler = MessageHandler(None, self.handle_message)
        self.app.add_handler(message_handler)

        self.app.run_polling()


# Start Bot Script
if __name__ == "__main__":
    bot = MyBot(os.getenv("TELEGRAM_KEY"))
    asyncio.run(bot.run())
    