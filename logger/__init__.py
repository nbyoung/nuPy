from logging import logging

DEBUG   = logging.DEBUG
INFO    = logging.INFO
WARNING = logging.WARNING
ERROR   = logging.ERROR
CRITICAL = logging.CRITICAL

def set(level=INFO):
    logging.basicConfig(level=level)

_logger = None

def get(label=__name__):
    global _logger
    if _logger == None:
        _logger = logging.getLogger(label)
    return _logger
