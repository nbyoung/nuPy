try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
import service

from MicroWebSrv2 import MicroWebSrv2, MicroWebSrv2Exception

class ServiceError(OSError): pass

class Service(service.Service):

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
    
    async def onLoop(self, stopCallback):
        if not self._mws2.IsRunning: stopCallback()
        await asyncio.sleep(1)

    async def onStop(self):
        self._mws2.Stop()
