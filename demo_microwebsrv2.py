try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
import configuration
import logger
import service
import tmp

from services import network
from services.microwebsrv2 import Service as MicroWebSrv2Service
from server import Server

class OperatingService(service.Service):

    def __init__(self, networkStatus, period=10.0):
        self._networkStatus = networkStatus
        self._period = period

    async def loop(self, stopCallback):
        async with self._networkStatus.setter as setter:
            isDHCP = setter.get('is_dhcp')
            isDHCP = not isDHCP
            setter.set('is_dhcp', isDHCP)
            log.info('DHCP' if isDHCP else 'Static')
        await asyncio.sleep(self._period)

async def _amain(port):
    with tmp.Path('network.json') as networkPath:
        networkStatus = network.Status(networkPath)
        stopService, results = await service.Runner(
        ).add(
            network.Service(networkStatus)
        ).add(
            MicroWebSrv2Service(port=Server.port, root=Server.root)
        ).add(
            OperatingService(networkStatus)
        ).run()
        log.info('%s %s', stopService.__class__.__name__, results or '')

def main(port=80, level=logger.INFO):
    global log
    logger.set(level=level)
    log = logger.get('modbus')
    try:
        asyncio.run(_amain(port))
    except KeyboardInterrupt:
        pass

def debug():
    main(8000, level=logger.DEBUG)
    
#main()
debug()
