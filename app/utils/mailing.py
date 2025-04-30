import logging
import os
from datetime import datetime, timedelta

from aiogram import Bot

from app.database.db import get_db_connection, get_list_requests
from app.keyboards.inline import combined_kb
from app.lexicon.lexicon import LEXICON
from app.config_data.config import load_config

config = load_config()

logger = logging.getLogger('lomportbot.mailing')


async def monthly_mailing(bot: Bot):
    logger.debug("Запуск задачи рассылки...")
    db_conn = await get_db_connection()
    try:
        with db_conn.cursor() as cur:
            # Получаем список всех пользователей
            cur.execute("SELECT user_id FROM telegram_bot_users")
            users = cur.fetchall()
            logger.debug(f"Найдено {len(users)} пользователей для рассылки.")

            # Отправляем сообщение каждому пользователю
            for user in users:
                try:
                    await bot.send_message(chat_id=user[0], text=LEXICON['mailing_list_text'],
                                           reply_markup=combined_kb)
                    logger.debug(f"Сообщение отправлено пользователю {user[0]}.")
                except Exception as e:
                    logger.error(f"Ошибка при отправке сообщения пользователю {user[0]}: {e}")

            logger.info("Рассылка завершена.")
    except Exception as e:
        logger.exception("Ошибка при выполнении задачи рассылки: %s", e)
    finally:
        db_conn.close()


async def daily_report(bot: Bot):
    """
    Формирует и отправляет ежедневный отчет администраторам.
    """
    logger.debug("Запуск задачи: ежедневный отчет")

    try:
        # Получаем текущую дату
        today = datetime.now().strftime('%Y-%m-%d')  # Формат: '2025-03-18'
        # Получаем вчерашнюю дату
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')  # Формат: '2025-03-17'

        # Получаем количество обработанных запросов за сегодня
        number_of_requests_processed = len(get_list_requests(date_from=yesterday, date_to=today))

        # Формируем текст отчета
        report_text = LEXICON['daily_report_text'].format(yesterday, number_of_requests_processed)

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
