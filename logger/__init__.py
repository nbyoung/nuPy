from logging import logging

DEBUG   = logging.DEBUG
INFO    = logging.INFO
WARNING = logging.WARNING
ERROR   = logging.ERROR
CRITICAL = logging.CRITICAL

def set(level=INFO):
    logging.basicConfig(level=level)

def get(label):
    return logging.getLogger(label)
