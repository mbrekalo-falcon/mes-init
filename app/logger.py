from . import settings
from .settings import BASE_DIR

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s:%(name)s: %(message)s '
                      '(%(asctime)s; %(filename)s:%(lineno)d)',
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'tempname': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Only log to local file in local setup, AWS logging takes care of logging to the console.
# if settings.DEBUG:
# temporary set to log everything:
LOGGING['handlers']['file'] = {
        'level': 'INFO',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': BASE_DIR + '/log/tempname.log',
        'maxBytes': 1024 * 1024 * 10,
        'formatter': 'verbose',
        'backupCount': 30,
    }
LOGGING['loggers'] = {
    'tempname': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
        'propagate': True,
    },
}
