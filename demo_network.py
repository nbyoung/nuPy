try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
import configuration
import logger
import service
from services import network
import tmp

class AdminService(service.Service):

    def __init__(self, runner, networkStatus, period=10.0):
        super().__init__(runner)
        self._networkStatus = networkStatus
        self._period = period

    async def loop(self, stopCallback):
        async with self._networkStatus.setter as setter:
            isDHCP = setter.get('is_dhcp')
            setter.set('is_dhcp', not isDHCP)
        await asyncio.sleep(self._period)

async def _amain():
    with tmp.Path('network.json') as networkPath:
        networkStatus = network.Status(networkPath)
        stopService, results = await service.Runner(
        ).add(
            AdminService, networkStatus
        ).add(
            network.Service, networkStatus
        ).run()
        log.info('%s %s', stopService.__class__.__name__, results or '')

def main(level=logger.INFO):
    global log
    logger.set(level=level)
    log = logger.get('service')
    try:
        asyncio.run(_amain())
    except KeyboardInterrupt:
        pass

def debug():
    main(level=logger.DEBUG)
    
main()
