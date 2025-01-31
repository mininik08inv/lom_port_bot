import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, ChatMemberUpdatedFilter, KICKED, MEMBER
from aiogram.types import ContentType
from aiogram import F

from app.handlers.commands import process_start_command, process_help_command, process_list_pzu_command, if_the_photo, \
    if_the_sticker, if_the_voice, if_something_else, send_point, process_user_unblocked_bot, process_user_blocked_bot

import logging.config
from loggs.logging_setting import logging_config

logging.config.dictConfig(logging_config)
logger = logging.getLogger('bot')

# BOT_TOKEN = os.environ.get('TELEGRAM_TOKEN')
BOT_TOKEN = os.environ.get('COURSE_TEST_BOT_TOKEN')

# Создаем объекты бота и диспетчера
dp: Dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Регистрируем хэндлеры
dp.message.register(process_start_command, Command(commands='start'))
dp.message.register(process_help_command, Command(commands='help'))
dp.message.register(process_list_pzu_command, Command(commands='list_pzu'))
dp.message.register(if_the_photo, F.content_type == ContentType.PHOTO)
dp.message.register(if_the_sticker, F.content_type == ContentType.STICKER)
dp.message.register(if_the_voice, F.content_type == ContentType.VOICE)
dp.message.register(if_something_else, F.content_type.in_({ContentType.VIDEO_NOTE,
                                                           ContentType.AUDIO,
                                                           ContentType.DOCUMENT,
                                                           ContentType.GAME,
                                                           ContentType.UNKNOWN,
                                                           ContentType.ANY
                                                           }))
dp.my_chat_member.register(process_user_blocked_bot, ChatMemberUpdatedFilter(member_status_changed=KICKED))
dp.my_chat_member.register(process_user_unblocked_bot, ChatMemberUpdatedFilter(member_status_changed=MEMBER))
dp.message.register(send_point)

if __name__ == '__main__':
    dp.run_polling(bot)
