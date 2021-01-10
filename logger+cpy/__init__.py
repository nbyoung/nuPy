import sys
import logging

DEBUG   = logging.DEBUG
INFO    = logging.INFO
WARNING = logging.WARNING
ERROR   = logging.ERROR
CRITICAL = logging.CRITICAL

def set(level=INFO):
    try:
        logging.basicConfig(level=level, force=True)
    except ValueError:
        logging.basicConfig(level=level)

def get(label):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
    logger = logging.getLogger(label)
    if not logger.hasHandlers(): logger.addHandler(handler)
    return logger
