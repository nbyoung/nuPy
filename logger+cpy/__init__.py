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

_logger = None

def get(label=__name__):
    global _logger
    if _logger == None:
        _logger = logging.getLogger(label)
        # if not _logger.hasHandlers():
        #     handler = logging.StreamHandler(sys.stdout)
        #     handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
        #     _logger.addHandler(handler)
    return _logger
