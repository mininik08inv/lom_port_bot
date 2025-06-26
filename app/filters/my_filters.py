from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from app.database.db import list_directions, get_list_pzu

import logging

logger = logging.getLogger(__name__)
print(logger)


async def direction_filter(callback: CallbackQuery) -> bool:
    logger.debug("работает фильтр direction_filter")
    """Фильтр для проверки, что callback.data - это существующее направление"""
    directions = await list_directions()
    return callback.data in directions


async def pzu_filter(callback: CallbackQuery) -> bool:
    logger.debug("работает фильтр pzu_filter")
    """Фильтр для проверки, что callback.data - это существующее pzu"""
    list_pzu = await get_list_pzu()
    return callback.data in list_pzu
