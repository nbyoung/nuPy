import os
import sys

if sys.implementation.name == 'micropython':
    import uasyncio as asyncio
else:
    import asyncio

import configuration

class Service:

    async def start(self):
        pass

    async def _run(self, runner):
        def onStop():
            runner._doRun = False
            runner._stop(self)
        while runner._doRun:
            await self.loop(onStop)
        return await self.onStop()

    async def onStop(self): raise NotImplementedError

class Runner:

    def __init__(self):
        self._services = []
        self._doRun = True
        self._stopService = None

    def add(self, service):
        self._services.append(service)
        return self
        
    async def run(self):
        await asyncio.gather(
            *[s.start() for s in self._services]
        )
        results = await asyncio.gather(
            *[s._run(self) for s in self._services]
        )
        return self._stopService, results

    def _stop(self, service):
        self._stopService = service
