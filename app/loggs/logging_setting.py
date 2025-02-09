import sys
import os

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
            'level': 'DEBUG',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'formatter_1',
            'stream': 'ext://sys.stdout'
        },
        'bot_stopped': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'formatter_1',
            'stream': 'ext://sys.stdout'
        },
    },
    'loggers': {
        'lomportbot': {
            'handlers': ['save_request_handler', 'console'],
            'level': 'DEBUG',
        },
    },

}
