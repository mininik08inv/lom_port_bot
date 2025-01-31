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
    },
    'loggers': {
        'bot': {
            'handlers': ['save_request_handler', ],
            'level': 'DEBUG',
        },
        'app.handlers.commands': {
            'handlers': ['save_request_handler', ],
            'level': 'DEBUG',
        },
        'app.utils.generating_a_reply_message': {
            'handlers': ['save_request_handler', ],
            'level': 'DEBUG',
        }
    },

}
