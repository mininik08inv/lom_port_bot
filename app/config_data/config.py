import os
from dataclasses import dataclass
from typing import Optional

from environs import Env


@dataclass
class DatabaseConfig:
    database: str  # Название базы данных
    db_host: str  # URL-адрес базы данных
    db_user: str  # Username пользователя базы данных
    db_password: str  # Пароль к базе данных


@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту
    admin_ids: list[int]  # Список id администраторов бота


@dataclass
class YooKassa:
    account_id: str
    secret_key: str


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig
    yoo_kassa: YooKassa


def load_config(path: Optional[str] = None) -> Config:
    """Загружает конфиг из .env-файла.
    Если path не указан, выбирает .env_prod или .env автоматически.
    """
    # Автоматический выбор файла, если path не задан
    if path is None:
        path = ".env_prod" if os.getenv("PRODUCTION", "").lower() == "true" else ".env"

    env = Env()
    env.read_env(path)  # Загружаем переменные из файла
    # print(path)

    return Config(
        tg_bot=TgBot(
            token=env("TELEGRAM_TOKEN"), admin_ids=list(map(int, env.list("ADMIN_IDS")))
        ),
        db=DatabaseConfig(
            database=env("POSTGRES_DB"),
            db_host=env("POSTGRES_HOST"),
            db_user=env("POSTGRES_USER"),
            db_password=env("POSTGRES_PASSWORD"),
        ),
        yoo_kassa=YooKassa(
            account_id=env("YOOKASSA_ACCOUNT_ID"), secret_key=env("YOOKASSA_SECRET_KEY")
        ),
    )
