import logging
from datetime import datetime, timedelta

from aiogram import Bot

from app.database.db import get_db_connection, get_list_requests
from app.keyboards.inline import combined_kb
from app.lexicon.lexicon import LEXICON
from app.config_data.config import load_config

config = load_config()

logger = logging.getLogger("lomportbot.mailing")


async def monthly_mailing(bot: Bot):
    logger.debug("Запуск задачи рассылки...")
    db_conn = await get_db_connection()
    try:
        # Для asyncpg не нужно явно создавать курсор для простых запросов
        users = await db_conn.fetch("SELECT user_id FROM telegram_bot_users")
        logger.debug(f"Найдено {len(users)} пользователей для рассылки.")

        for user in users:
            if user["user_id"] == 379228746:
                logger.info("Пропускаем: ", user["user_id"])
                continue
            try:
                await bot.send_message(
                    chat_id=user["user_id"],
                    text=LEXICON["mailing_list_text"],
                    reply_markup=combined_kb,
                )
                logger.debug(f"Сообщение отправлено пользователю {user['user_id']}.")
            except Exception as e:
                logger.error(f"Ошибка при отправке пользователю {user['user_id']}: {e}")

        logger.info("Рассылка завершена.")
    except Exception as e:
        logger.exception(f"Ошибка при выполнении задачи рассылки: {e}")
    finally:
        await db_conn.close()


async def daily_report(bot: Bot):
    """
    Формирует и отправляет ежедневный отчет администраторам.
    """
    logger.debug("Запуск задачи: ежедневный отчет")

    try:
        # Получаем текущую дату
        today = datetime.now()
        # Получаем вчерашнюю дату
        yesterday = datetime.now() - timedelta(days=1)

        # Получаем количество обработанных запросов за сегодня
        len_list_request = await get_list_requests(date_from=yesterday, date_to=today)
        number_of_requests_processed = len(len_list_request)

        # Формируем текст отчета
        report_text = LEXICON["daily_report_text"].format(
            yesterday.strftime("%Y-%m-%d"), number_of_requests_processed
        )

        # Отправляем сообщение каждому администратору
        for admin_id in config.tg_bot.admin_ids:
            try:
                await bot.send_message(chat_id=admin_id, text=report_text)
                logger.debug(f"Сообщение отправлено админу {admin_id}.")
            except Exception as e:
                logger.error(f"Ошибка при отправке сообщения админу {admin_id}: {e}")

        logger.debug("Отправка ежедневного отчета завершена.")
    except Exception as e:
        logger.exception(f"Ошибка при выполнении задачи 'ежедневный отчет': {e}")
