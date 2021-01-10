import sys
import logging

DEBUG   = logging.DEBUG
INFO    = logging.INFO
WARNING = logging.WARNING
ERROR   = logging.ERROR
CRITICAL = logging.CRITICAL

def get(label, level=INFO):
    logging.basicConfig(level=level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
    logger = logging.getLogger(label)
    if not logger.hasHandlers(): logger.addHandler(handler)
    return logger
