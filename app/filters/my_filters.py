from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from app.database.db import list_directions

import logging

logger = logging.getLogger(__name__)


class IsValidAmount(BaseFilter):
    logger.debug('работает фильтр IsValidAmount')
    async def __call__(self, message: Message) -> bool:
        if not message.text.isdigit():
            return False
        return 10 <= int(message.text) <= 100000

async def direction_filter(callback: CallbackQuery) -> bool:
    logger.debug('работает фильтр IsValidAmount')
    """Фильтр для проверки, что callback.data - это существующее направление"""
    directions = await list_directions()
    return callback.data in directions