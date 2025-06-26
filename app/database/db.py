import asyncpg
from datetime import datetime
from app.config_data.config import load_config
import logging

logger = logging.getLogger("lomportbot.db")

config = load_config()


async def get_db_connection():
    """Функция возвращает соединение с базой данных"""
    db_conn = await asyncpg.connect(
        host=config.db.db_host,
        database=config.db.database,
        user=config.db.db_user,
        password=config.db.db_password,
        # port=config.db.db_port  # Укажите порт базы данных
    )
    return db_conn


async def execute_query(connection, query: str, *args):
    """Функция выполняет запрос к базе данных"""
    try:
        result = await connection.fetch(query, *args)
        return result
    except Exception as e:
        logger.exception("Ошибка при выполнении запроса: %s", e)
        return None


async def query_item_in_database(item: str):
    """Запрос информации о пункте по его аббревиатуре"""
    db_conn = await get_db_connection()
    try:
        sql_query = "SELECT name, abbreviation, lat, lon, phone FROM points_location WHERE abbreviation=$1"
        res_data = await db_conn.fetchrow(sql_query, item)
        return res_data
    except Exception as e:
        logger.exception("Ошибка в получении пункта из базы данных: %s", e)
    finally:
        await db_conn.close()


async def list_directions():
    """Функция возвращает список направлений"""
    db_conn = await get_db_connection()
    try:
        query = """SELECT title FROM points_direction 
                   WHERE id IN (SELECT direction_id FROM points_location 
                               WHERE direction_id IS NOT NULL)"""
        result = await db_conn.fetch(query)
        return [
            row["title"] for row in result
        ]  # возвращаем список из названий направлений
    finally:
        await db_conn.close()


async def list_pzu_in_direction(direction: str):
    """Функция возвращает список ПЗУ в направлении"""
    db_conn = await get_db_connection()
    try:
        direction_id = await db_conn.fetchval(
            "SELECT id FROM points_direction WHERE title = $1;", direction
        )

        result = await db_conn.fetch(
            "SELECT abbreviation FROM points_location WHERE direction_id = $1;",
            direction_id,
        )

        return [row["abbreviation"] for row in result]
    finally:
        await db_conn.close()


async def get_list_pzu():
    """Функция возвращает список аббревиатур ПЗУ"""
    db_conn = await get_db_connection()
    try:
        result = await db_conn.fetch("SELECT abbreviation FROM points_location")
        return [row["abbreviation"] for row in result]
    finally:
        await db_conn.close()


async def add_id_to_database(user_id: int):
    """Добавление ID пользователя в базу данных"""
    if not isinstance(user_id, int):
        raise TypeError("user_id должен быть целым числом")

    db_conn = await get_db_connection()
    try:
        # Проверяем, есть ли уже этот ID в базе данных
        user = await db_conn.fetchrow(
            "SELECT * FROM telegram_bot_users WHERE user_id = $1", user_id
        )

        # Если ID нет в базе данных, добавляем его
        if user is None:
            await db_conn.execute(
                """
                INSERT INTO telegram_bot_users (user_id)
                VALUES ($1)
                ON CONFLICT (user_id) DO NOTHING
            """,
                user_id,
            )
            logger.info(f"Пользователь {user_id} добавлен в базу данных.")
    except Exception as e:
        logger.exception("Ошибка при добавлении user_id в бд: %s", e)
    finally:
        await db_conn.close()


async def delete_id_to_database(user_id: int):
    """Удаление ID пользователя из базы данных"""
    db_conn = await get_db_connection()
    try:
        await db_conn.execute(
            "DELETE FROM telegram_bot_users WHERE user_id = $1", user_id
        )
        logger.info(f"Пользователь {user_id} удален из базы данных.")
    except Exception as e:
        logger.exception(f"Ошибка при удалении user_id из базы данных: {e}")
    finally:
        await db_conn.close()


async def get_list_requests(date_from=None, date_to=None):
    """
    Получает список запросов из таблицы bot_logs за указанный период.

    :param date_from: Начальная дата периода (в формате 'YYYY-MM-DD'). Если не указана, используется '2025-03-01'.
    :param date_to: Конечная дата периода (в формате 'YYYY-MM-DD'). Если не указана, используется текущая дата.
    :return: Список словарей с данными запросов.
    """
    if date_from is None:
        date_from = "2025-03-01"
    if date_to is None:
        date_to = datetime.now().strftime("%Y-%m-%d")

    db_conn = await get_db_connection()
    try:
        query = """
            SELECT log_level, log_time, filename, message, user_id, user_name, fullname, pzu_name
            FROM bot_logs
            WHERE log_time >= $1 AND log_time <= $2
            ORDER BY log_time ASC
        """
        results = await db_conn.fetch(query, date_from, date_to)

        requests = []
        for row in results:
            requests.append(
                {
                    "log_level": row["log_level"],
                    "log_time": row["log_time"],
                    "filename": row["filename"],
                    "message": row["message"],
                    "user_id": row["user_id"],
                    "user_name": row["user_name"],
                    "fullname": row["fullname"],
                    "pzu_name": row["pzu_name"],
                }
            )
        return requests
    except Exception as e:
        logger.error(f"Ошибка при получении списка запросов: {e}")
        return []
    finally:
        await db_conn.close()
