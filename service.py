import os
import sys

if sys.implementation.name == 'micropython':
    import uasyncio as asyncio
else:
    import asyncio

import configuration

class Service:

    def __init__(self, runner):
        self._runner = runner

    async def _run(self, service):
        def onStop():
            self._runner._doRun = False
            self._runner._stop(service)
        while self._runner._doRun:
            await self.loop(onStop)
        return await self.onStop()

    async def onStop(self):
        pass

class Runner:

    def __init__(self):
        self._services = []
        self._doRun = True
        self._stopService = None

    def add(self, serviceClass, *args, **kwargs):
        self._services.append(serviceClass(self, *args, **kwargs))
        return self
        
    async def run(self):
        results = await asyncio.gather(
            *[s._run(s) for s in self._services]
        )
        return self._stopService, results

    def _stop(self, service):
        self._stopService = service
