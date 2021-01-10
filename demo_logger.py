import logger

def main():
    for level in (
            logger.DEBUG,
            logger.INFO,
            logger.WARNING,
            logger.ERROR,
            logger.CRITICAL,
    ):
        logger.set(level=level)
        number = 0
        for method in ('debug', 'info', 'warning', 'error', 'critical', ):
            log = logger.get('demo')
            getattr(log, method)('%s %d', *(str(level) * level, number))
            number += 1
    
main()
