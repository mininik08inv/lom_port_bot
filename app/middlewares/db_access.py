from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable
import logging
from app.database.db import get_db_connection  # Импортируйте ваш коннектор к БД

logger = logging.getLogger("lomportbot")


class DBAccessMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id = event.event.from_user.id

        db_conn = await get_db_connection()
        try:
            # Проверяем, есть ли уже этот ID в базе данных
            user = await db_conn.fetchrow(
                "SELECT * FROM telegram_bot_users WHERE user_id = $1", user_id
            )

            # Если ID нет в базе данных,
            if not user:
                logger.info(f"Доступ запрещен для пользователя {user_id}")
                await event.event.answer("⛔ Доступ к боту ограничен")
                return

        except Exception as e:
            logger.error(f"Ошибка при работе с базой данных: {e}")

        finally:
            await db_conn.close()

        result = await handler(event, data)

        return result
