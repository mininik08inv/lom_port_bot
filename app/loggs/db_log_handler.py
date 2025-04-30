import asyncio
import logging
import asyncpg
from datetime import datetime
from app.database.db import get_db_connection, execute_query

logger = logging.getLogger('lomportbot.db_log_handler')


class AsyncPostgresHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.connection = None

    async def connect(self):
        """Устанавливаем соединение с базой данных"""
        if not self.connection or self.connection.is_closed():
            self.connection = await get_db_connection()

    def emit(self, record):
        """Асинхронная запись лога"""
        asyncio.create_task(self._async_emit(record))

    async def _async_emit(self, record):
        """Реальная асинхронная запись"""
        try:
            await self.connect()
            q = 1 / 0
            await execute_query(self.connection,
                                """
                INSERT INTO bot_logs (
                    log_level, 
                    log_time, 
                    filename, 
                    message, 
                    user_id, 
                    user_name, 
                    fullname, 
                    pzu_name
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                                record.levelname,
                                datetime.now(),
                                record.filename,
                                record.getMessage(),
                                getattr(record, 'user_id', None),
                                getattr(record, 'user_name', None),
                                getattr(record, 'fullname', None),
                                getattr(record, 'pzu_name', None)
                                )
        except Exception as e:
            logger.info(f"Ошибка записи лога: {e}")
