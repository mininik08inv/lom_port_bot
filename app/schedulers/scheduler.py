from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from app.utils.mailing import monthly_mailing, daily_report
import logging

logger = logging.getLogger('lomportbot.scheduler')


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    # Логируем запуск планировщика
    logger.info("Настройка планировщика...")

    # Настройка задачи для рассылки
    scheduler.add_job(
        monthly_mailing,
        "cron",
        day=30,
        hour=10,
        minute=16,
        # "interval",
        # seconds=20,
        args=(bot,),
        id="monthly_mailing",  # Уникальный идентификатор задачи
    )
    # Логируем добавление задачи
    logger.debug("Задача 'monthly_mailing' добавлена в планировщик.")

    scheduler.add_job(
        daily_report,
        "cron",
        hour=15,
        minute=00,
        # "interval",
        # seconds=15,
        args=(bot,),
        id="daily_report",  # Уникальный идентификатор задачи
    )
    logger.debug("Задача 'daily_report' добавлена в планировщик.")

    return scheduler
