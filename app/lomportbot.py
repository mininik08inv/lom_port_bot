import sys
sys.path.append('./app/')

import asyncio
import logging.config

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from handlers import commands, callback_directions
from keyboards.set_menu import set_main_menu

from app.loggs.logging_setting import logging_config
from app.config_data.config import load_config

logging.config.dictConfig(logging_config)
logger = logging.getLogger('lomportbot')

async def main():
    config = load_config('.env')

    BOT_TOKEN = config.tg_bot.token

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(commands.router)
    dp.include_router(callback_directions.router)

    await set_main_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

logger.info('Bot started')
asyncio.run(main())
logger.info('Bot stopped')
