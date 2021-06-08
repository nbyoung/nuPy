try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
import configuration
import logger
import service
import lan
import tmp

class OperatingService(service.Service):

    def __init__(self, lanStatus, period=10.0):
        self._lanStatus = lanStatus
        self._period = period

    async def onLoop(self, stopCallback):
        async with self._lanStatus.setter as setter:
            isDHCP = setter.get('is_dhcp')
            isDHCP = not isDHCP
            setter.set('is_dhcp', isDHCP)
            log.info('DHCP' if isDHCP else 'Static')
        await asyncio.sleep(self._period)

async def _amain():
    with tmp.Path('lan.json') as lanPath:
        lanStatus = configuration.Status(lan.JSONStore(lanPath))
        stopService, results = await service.Runner(
        ).add(
            OperatingService(lanStatus)
        ).add(
            lan.Service(lanStatus)
        ).run()
        log.info('%s %s', stopService.__class__.__name__, results or '')

def main(level=logger.INFO):
    global log
    logger.set(level=level)
    log = logger.get('lan')
    try:
        asyncio.run(_amain())
    except KeyboardInterrupt:
        pass

def debug():
    main(level=logger.DEBUG)
    
main()
