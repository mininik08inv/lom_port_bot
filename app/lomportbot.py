# main.py
import asyncio
import logging.config
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from handlers import commands, callback_directions
from keyboards.set_menu import set_main_menu
from app.loggs.logging_setting import logging_config
from app.config_data.config import load_config
from schedulers.scheduler import setup_scheduler  # Импортируем планировщик

logging.config.dictConfig(logging_config)
logger = logging.getLogger('lomportbot')

async def main():
    config = load_config('.env')
    BOT_TOKEN = config.tg_bot.token
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Настройка планировщика
    logger.info("Запуск планировщика...")
    scheduler = setup_scheduler(bot)
    scheduler.start()
    logger.info("Планировщик запущен.")

    dp.include_router(commands.router)
    dp.include_router(callback_directions.router)
    await set_main_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info('Бот запущен')
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception("Ошибка при запуске бота: %s", e)
    finally:
        logger.info('Бот остановлен')