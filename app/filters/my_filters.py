from aiogram.filters import BaseFilter
from aiogram.types import Message

class IsValidAmount(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.text.isdigit():
            return False
        return 10 <= int(message.text) <= 100000