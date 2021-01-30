try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
from collections import namedtuple
import logger
import select
import service
import socket
import struct

from MicroWebSrv2  import MicroWebSrv2

class ServiceError(OSError): pass

class Service(service.Service):

    _log = logger.get()

    # TODO serverStatus: client address, bytes received
    def __init__(self, root='/flash/www', port=80):
        self._mws2 = MicroWebSrv2()
        self._mws2.BindAddress = ('0.0.0.0', port)
        self._mws2.SetEmbeddedConfig()
        self._mws2.RootPath = root
        HOME = '/'
        if not self._mws2.ResolvePhysicalPath(HOME):
            raise MicroWebSrv2Exception(
                "RootPath '%s' does not resolve with URL '%s'"
                % (self._mws2.RootPath, HOME)
            )
        self._mws2.NotFoundURL = HOME
        self._mws2.StartManaged()
    
    async def loop(self, stopCallback):
        if not self._mws2.IsRunning: stopCallback()
        await asyncio.sleep(1)

    async def onStop(self):
        self._mws2.stop()
