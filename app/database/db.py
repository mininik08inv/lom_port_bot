import psycopg
from datetime import datetime
from app.config_data.config import load_config
import logging

logger = logging.getLogger('lomportbot.db')

config = load_config('.env_prod')


def get_db_connection():
    'Функция возвращает соединение с базой данных'
    db_conn = psycopg.connect(
        host=config.db.db_host,
        dbname=config.db.database,
        user=config.db.db_user,
        password=config.db.db_password,
        # port=config.db.db_port  # Укажите порт базы данных
    )
    return db_conn


def execute_query(connection, query: str, *args):
    'Функция выполняет запрос к базе данных'
    with connection.cursor() as cur:
        try:
            cur.execute(query, args)
            return cur.fetchall()
        except Exception as e:
            logger.exception("Ошибка при выполнении запроса: %s", e)


def query_item_in_database(item: str):
    db_conn = get_db_connection()
    with db_conn.cursor() as cur:
        sql_query = "SELECT name, abbreviation, lat, lon, phone FROM points_location WHERE abbreviation=%s"
        try:
            cur.execute(sql_query, (item,))
            res_data = cur.fetchone()
            return res_data
        except Exception as e:
            logger.exception("Ошибка в получении пункта из базы данных: %s", e)


def list_directions():
    'Функция возвращает список направлений'
    db_conn = get_db_connection()
    return execute_query(db_conn,
                         'SELECT title FROM points_direction WHERE id IN (SELECT direction_id FROM points_location WHERE direction_id IS NOT NULL)')


def list_pzu_in_direction(direction: str):
    'Функция возвращает список ПЗУ в направлении'
    db_conn = get_db_connection()
    direction_id = execute_query(db_conn, 'select id from points_direction where title = %s;', direction)[0][0]
    result_request = execute_query(db_conn, 'select abbreviation from points_location where direction_id = %s;',
                                   direction_id)
    result = [i[0] for i in result_request]
    return result


def list_pzu():
    'Функция возвращает список аббревиатур ПЗУ'
    db_conn = get_db_connection()
    result_request = execute_query(db_conn, 'select abbreviation from points_location')
    result = [i[0] for i in result_request]
    return result


def add_id_to_database(user_id: int):
    if not isinstance(user_id, int):
        raise TypeError("user_id должен быть целым числом")


    db_conn = get_db_connection()
    with db_conn.cursor() as cur:
        try:
            # Проверяем, есть ли уже этот ID в базе данных
            cur.execute("SELECT * FROM telegram_bot_users WHERE user_id = %s", (user_id,))
            user = cur.fetchone()
            # Если ID нет в базе данных, добавляем его
            if user is None:
                cur.execute("""
                        INSERT INTO telegram_bot_users (user_id)
                        VALUES (%s)
                        ON CONFLICT (user_id) DO NOTHING
                    """, (user_id,))
                db_conn.commit()
                logger.info(f"Пользователь {user_id} добавлен в базу данных.")
        except Exception as e:
            logger.exception("Ошибка при добавлении user_id в бд: %s", e)


def delete_id_to_database(user_id):
    db_conn = get_db_connection()
    with db_conn.cursor() as cur:
        try:
            # Удаляем пользователя из базы данных
            cur.execute("DELETE FROM telegram_bot_users WHERE user_id = %s", (user_id,))
            db_conn.commit()
            logger.info(f"Пользователь {user_id} удален из базы данных.")
        except Exception as e:
            logger.exception(f"Ошибка при удалении user_id из базы данных: {e}")

def get_list_requests(date_from=None, date_to=None):
    """
    Получает список запросов из таблицы bot_logs за указанный период.

    :param date_from: Начальная дата периода (в формате 'YYYY-MM-DD'). Если не указана, используется '2025-03-01'.
    :param date_to: Конечная дата периода (в формате 'YYYY-MM-DD'). Если не указана, используется текущая дата.
    :return: Список словарей с данными запросов.
    """
    # Устанавливаем значения по умолчанию, если параметры не переданы
    if date_from is None:
        date_from = '2025-03-01'  # Начальная дата по умолчанию
    if date_to is None:
        date_to = datetime.now().strftime('%Y-%m-%d')  # Текущая дата по умолчанию

    try:
        # Подключаемся к базе данных
        with get_db_connection() as connection:
            with connection.cursor() as cur:
                # Формируем SQL-запрос
                query = """
                    SELECT log_level, log_time, filename, message, user_id, user_name, fullname, pzu_name
                    FROM bot_logs
                    WHERE log_time >= %s AND log_time <= %s
                    ORDER BY log_time ASC
                """
                # Выполняем запрос с параметрами
                cur.execute(query, (date_from, date_to))
                # Получаем результаты
                results = cur.fetchall()

                # Преобразуем результаты в список словарей
                requests = []
                for row in results:
                    requests.append({
                        'log_level': row[0],
                        'log_time': row[1],
                        'filename': row[2],
                        'message': row[3],
                        'user_id': row[4],
                        'user_name': row[5],
                        'fullname': row[6],
                        'pzu_name': row[7],
                    })

                return requests

    except Exception as e:
        # Логируем ошибку
        logger.error(f"Ошибка при получении списка запросов: {e}")
        return []
