import os
import logging
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes
from telegram.error import TelegramError
import asyncio
load_dotenv()
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class MyBot:
    def __init__(self, token):
        self.token = token
        self.bot = Bot(token=self.token)
        self.app = ApplicationBuilder().token(token).build()

    def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Soy un robotsin")

    def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message_text = update.message.text
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=message_text)

    async def send_evento(self, evento):
        try:
            mensaje= f"Nuevo evento detectado:\n\n{evento}"
            await self.bot.send_message(chat_id='1505812784', text=mensaje)
        except TelegramError as e:
            print(f'Error al enviar el mensaje: {e}')

    def run(self):
        start_handler = CommandHandler('start', self.start)
        self.app.add_handler(start_handler)

        message_handler = MessageHandler(None, self.handle_message)
        self.app.add_handler(message_handler)

        self.app.run_polling()


# Ejemplo de uso
if __name__ == '__main__':
    token = os.getenv('TELEGRAM_KEY')
    bot = MyBot(token)
    evento = "Se ha encontrado un evento"
    asyncio.run(bot.send_evento(evento))
