from logging.config import dictConfig
from .db_log_handler import AsyncPostgresHandler

# Конфигурация логгеров
logging_config = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'formatter_1': {
            'format': '#%(levelname)-8s [%(asctime)s] - %(filename)s:- %(message)s'
        },
    },
    'handlers': {
        'save_request_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'formatter_1',
            'filename': 'app/list_of_requests.log',
            'level': 'INFO',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'formatter_1',
            'stream': 'ext://sys.stdout'
        },
        'postgres': {
            '()': AsyncPostgresHandler,  # Используем наш AsyncPostgresHandler
            'level': 'DEBUG',
            'formatter': 'formatter_1',
        },
    },
    'loggers': {
        'lomportbot': {
            'handlers': ['save_request_handler', 'console'],  # Основной логгер
            'level': 'DEBUG',
        },
        'app': {
            'handlers': ['save_request_handler', 'console'],  # Основной логгер
            'level': 'DEBUG',
        },
        'db_logger': {
            'handlers': ['postgres'],  # Логгер для записи в базу данных
            'level': 'DEBUG',
            'propagate': False,  # Отключаем распространение логов
        },
    },
}

# Применяем конфигурацию
dictConfig(logging_config)
