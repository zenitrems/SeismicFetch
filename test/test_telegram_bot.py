import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from telegram.error import TelegramError

from src.telegram.telegram_bot import MyBot


class TestMyBot(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.bot_context = AsyncMock()
        self.bot_context.__aenter__.return_value = self.bot_context
        self.bot_context.__aexit__.return_value = False
        self.app = MagicMock()
        self.bot = MyBot(
            token="test-token",
            bot=self.bot_context,
            app=self.app,
            group_chat_id="group-id",
            error_chat_id="error-id",
        )

    async def test_start_sends_greeting(self):
        update = SimpleNamespace(effective_chat=SimpleNamespace(id=123))
        context = SimpleNamespace(bot=AsyncMock())

        await self.bot.start(update, context)

        context.bot.send_message.assert_awaited_once_with(
            chat_id=123, text="Soy un robotsin"
        )

    async def test_handle_message_echoes_text(self):
        update = SimpleNamespace(
            effective_chat=SimpleNamespace(id=321),
            message=SimpleNamespace(text="ping"),
        )
        context = SimpleNamespace(bot=AsyncMock())

        await self.bot.handle_message(update, context)

        context.bot.send_message.assert_awaited_once_with(chat_id=321, text="ping")

    async def test_send_update_sends_message_to_group(self):
        await self.bot.send_update("<b>alert</b>", [19.43, -99.13])

        self.bot_context.send_message.assert_awaited_once_with(
            chat_id="group-id", text="<b>alert</b>", parse_mode="HTML"
        )

    async def test_send_update_logs_telegram_errors(self):
        self.bot_context.send_message.side_effect = TelegramError("send failed")

        with patch("src.telegram.telegram_bot.logging.error") as logging_error:
            await self.bot.send_update("<b>alert</b>", [19.43, -99.13])

        logging_error.assert_called_once()

    async def test_send_error_sends_escaped_error_message(self):
        await self.bot.send_error("bad <tag>")

        self.bot_context.send_message.assert_awaited_once_with(
            chat_id="error-id",
            text="<b>ERROR</b>\n\n<code>bad &lt;tag&gt;</code>",
            parse_mode="HTML",
        )

    async def test_send_error_logs_telegram_errors(self):
        self.bot_context.send_message.side_effect = TelegramError("send failed")

        with patch("src.telegram.telegram_bot.logger.error") as logger_error:
            await self.bot.send_error("boom")

        logger_error.assert_called_once()


if __name__ == "__main__":
    unittest.main()
