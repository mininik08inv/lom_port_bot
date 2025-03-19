from datetime import datetime
import pytest
from aiogram import Dispatcher, Bot
from aiogram.types import Message, User, Chat, Update
from aiogram.filters import Command
from unittest.mock import AsyncMock
from app.handlers.commands import process_start_command

@pytest.mark.asyncio
async def test_process_start_command():
    # Создаем мок-объект бота
    bot = AsyncMock(spec=Bot)

    # Создаем диспетчер
    dp = Dispatcher()

    # Регистрируем хэндлер
    dp.message.register(process_start_command, Command("start"))

    # Создаем мок-объект сообщения
    message = Message(
        message_id=1,
        date=datetime.now(),
        chat=Chat(id=1, type="private"),
        from_user=User(id=1, is_bot=False, first_name="Test"),
        text="/start",
    )

    # Эмулируем обработку сообщения
    update = Update(update_id=1, message=message)
    await dp.feed_update(bot, update=update)

    # Логируем вызовы метода send_message
    print("Calls to send_message:", bot.send_message.mock_calls)

    # Проверяем, что бот вызвал метод answer с правильным текстом
    bot.send_message.assert_called_once_with(chat_id=1, text="Привет!")