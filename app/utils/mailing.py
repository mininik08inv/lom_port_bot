import logging
from aiogram import Bot
from app.database.db import get_db_connection

logger = logging.getLogger('lomportbot.mailing')

async def mailing(bot: Bot):
    logger.info("Запуск задачи рассылки...")
    db_conn = get_db_connection()
    try:
        with db_conn.cursor() as cur:
            # Получаем список всех пользователей
            cur.execute("SELECT user_id FROM telegram_bot_users")
            users = cur.fetchall()
            logger.info(f"Найдено {len(users)} пользователей для рассылки.")

            # Отправляем сообщение каждому пользователю
            for user in users:
                try:
                    await bot.send_message(chat_id=user[0], text="Тест рассылки каждые 15 секунд")
                    logger.debug(f"Сообщение отправлено пользователю {user[0]}.")
                except Exception as e:
                    logger.error(f"Ошибка при отправке сообщения пользователю {user[0]}: {e}")

            logger.info("Рассылка завершена.")
    except Exception as e:
        logger.exception("Ошибка при выполнении задачи рассылки: %s", e)
    finally:
        db_conn.close()