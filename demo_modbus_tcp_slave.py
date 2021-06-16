try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
import configuration
import logger
import service
import tmp

import modbus
from modbus import data, pdu, tcp, slave
from modbus.tcp.slave import Service as TCPService
import lan

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

class ProcessService(service.Service):

    def __init__(self, dataStatus):
        self._dataStatus = dataStatus

    async def onLoop(self, stopCallback):
        async with self._dataStatus.watcher as watcher:
            value0 = watcher.get(0)
            log.info('register[0]=%d', value0)

async def _amain(port):
    dataModel = data.Model((1, 2, 3, 4, 5))
    slave_ = slave.Slave(pdu.RequestHandler(dataModel, log.warning))
    with tmp.Path('lan.json') as lanPath:
        lanStatus = configuration.Status(lan.JSONStore(lanPath))
        stopService, results = await service.Runner(
        ).add(
            lan.Service(lanStatus)
        ).add(
            TCPService(slave.Handler(tcp.ADU, slave_), dataModel.status, port)
        ).add(
            ProcessService(dataModel.status)
        ).add(
            OperatingService(lanStatus)
        ).run()
        log.info('%s %s', stopService.__class__.__name__, results or '')

def main(port=502, level=logger.INFO):
    global log
    logger.set(level=level)
    log = logger.get('modbus')
    try:
        asyncio.run(_amain(port))
    except KeyboardInterrupt:
        pass

def debug():
    main(5502, level=logger.DEBUG)
    
main()
#debug()
