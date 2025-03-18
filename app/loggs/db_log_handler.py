import logging
from app.database.db import get_db_connection

logger = logging.getLogger('lomportbot.db_log_handler')

class PostgresHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.connection = get_db_connection()

    def emit(self, record):
        try:
            with get_db_connection() as connection:
                with connection.cursor() as cur:
                    query = """
                        INSERT INTO bot_logs (log_level, log_time, filename, message, user_id, user_name, fullname, pzu_name)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    log_time = self.formatter.formatTime(record, datefmt="%Y-%m-%d %H:%M:%S")
                    cur.execute(query, (
                        record.levelname,
                        log_time,
                        record.filename,
                        record.getMessage(),
                        getattr(record, 'user_id', None),
                        getattr(record, 'user_name', None),
                        getattr(record, 'fullname', None),
                        getattr(record, 'pzu_name', None),
                    ))
                    connection.commit()
        except Exception as e:
            logger.error(f"Ошибка при записи лога в базу данных: {e}")
            self.handleError(record)