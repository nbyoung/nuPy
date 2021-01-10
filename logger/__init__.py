from logging import logging

DEBUG   = logging.DEBUG
INFO    = logging.INFO
WARNING = logging.WARNING
ERROR   = logging.ERROR
CRITICAL = logging.CRITICAL

def get(label, level=INFO):
    logging.basicConfig(level=level)
    return logging.getLogger(label)
