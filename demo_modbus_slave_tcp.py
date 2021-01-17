try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
import configuration
import logger
import service
import tmp

from services.modbus.slave.tcp import Service as ModbusTCPService
from services.modbus.slave.tcp import Slave as ModbusTCPSlave
from services.modbus.slave.tcp import Handler as ModbusTCPHandler
from services.modbus import pdu, data

from services import network

class OperationService(service.Service):

    def __init__(self, runner, networkStatus, period=10.0):
        super().__init__(runner)
        self._networkStatus = networkStatus
        self._period = period

    async def loop(self, stopCallback):
        async with self._networkStatus.setter as setter:
            isDHCP = setter.get('is_dhcp')
            setter.set('is_dhcp', not isDHCP)
        await asyncio.sleep(self._period)

class ProcessService(service.Service):

    def __init__(self, runner, dataStatus):
        super().__init__(runner)
        self._dataStatus = dataStatus

    async def loop(self, stopCallback):
        async with self._dataStatus.watcher as watcher:
            value0 = watcher.get(0)
            log.info('register[0]=%d', value0)

async def _amain(port):
    modbusDataModel = data.Model((1, 2, 3, 4, 5))
    modbusTCPSlave = ModbusTCPSlave(pdu.Handler(modbusDataModel, log.warning))
    with tmp.Path('network.json') as networkPath:
        networkStatus = network.Status(networkPath)
        stopService, results = await service.Runner(
        ).add(
            network.Service, networkStatus
        ).add(
            ModbusTCPService, ModbusTCPHandler(modbusTCPSlave), modbusDataModel.status,
            port
        ).add(
            ProcessService, modbusDataModel.status
        ).add(
            OperationService, networkStatus
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
