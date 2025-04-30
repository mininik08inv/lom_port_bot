from datetime import datetime
import pytest
from aiogram import Dispatcher, Bot
from aiogram.types import Message, User, Chat, Update
from aiogram.filters import Command
from unittest.mock import AsyncMock, patch
from app.handlers.commands import process_start_command


@pytest.mark.asyncio
async def test_process_start_command():
    # 1. Создаем мок бота с правильной настройкой
    bot = AsyncMock(spec=Bot)
    bot.send_message = AsyncMock()  # Явно мокируем метод

    # 2. Инициализируем диспетчер
    dp = Dispatcher()

    # 3. Регистрируем обработчик
    dp.message.register(process_start_command, Command("start"))

    # 4. Создаем тестовые данные
    test_user = User(
        id=123,
        is_bot=False,
        first_name="Test",
        username="test_user"
    )
    test_chat = Chat(id=123, type="private")
    test_message = Message(
        message_id=1,
        date=datetime.now(),
        chat=test_chat,
        from_user=test_user,
        text="/start"
    )
    update = Update(update_id=1, message=test_message)

    # 5. Запускаем обработку
    await dp.feed_update(bot, update)

    # 6. Проверяем вызовы
    bot.send_message.assert_awaited_once()

    # Дополнительные проверки аргументов
    args, kwargs = bot.send_message.await_args
    assert kwargs['chat_id'] == 123
    assert "Привет" in kwargs['text']  # Проверяем часть текста