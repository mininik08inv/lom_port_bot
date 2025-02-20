import psycopg
from app.config_data.config import load_config
import logging

logger = logging.getLogger('lomportbot.db')

config = load_config('.env')


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
            print(res_data)
            return res_data
        except Exception as e:
            logger.exception("Ошибка в получении пункта из базы данных: %s", e)


def list_directions():
    'Функция возвращает список направлений'
    db_conn = get_db_connection()
    return execute_query(db_conn, 'select title from points_direction')


def list_pzu_in_direction(direction: str):
    'Функция возвращает список ПЗУ в направлении'
    db_conn = get_db_connection()
    direction_id = execute_query(db_conn, 'select id from points_direction where title = %s;', direction)[0][0]
    result_request = execute_query(db_conn, 'select abbreviation from points_location where direction_id = %s;',
                                   direction_id)
    result = [i[0] for i in result_request]
    return result


def list_pzu():
    'Функция возвращает список ПЗУ'
    db_conn = get_db_connection()
    result_request = execute_query(db_conn, 'select abbreviation from points_location')
    result = [i[0] for i in result_request]
    return result

# Инициализируем временную "базу данных"
users_db = []