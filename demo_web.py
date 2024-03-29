try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
from configuration import JSONStore
import logger
import service
import tmp

import lan
import web

import host

class PulseService(service.Service):

    def __init__(self, pulseStatus, period=2.0):
        self._pulseStatus = pulseStatus
        self._period = period

    async def onLoop(self, stopCallback):
        async with self._pulseStatus.setter as setter:
            isBeat = setter.get('is_beat')
            setter.set('is_beat', not isBeat)
        await asyncio.sleep(self._period / 2)

async def _amain():
    with tmp.Path('lan.json') as lanPath:
        api = web.API('/api/v0')
        lanStatus = api.add(
            'network', lan.JSONStore(lanPath)
        )
        pulseStatus = api.add(
            'pulse', JSONStore(None, '{ "is_beat": false }')
        )
        def exampleCallback(request, data):
            request.Response.ReturnOk("Hello, world! I'm a dynamic resource.")
        routeList = (
            web.Route('hello', web.HTTP.GET, '/hello', exampleCallback, None),
        )
        stopService, results = await service.Runner(
        ).add(
            lan.Service(lanStatus)
        ).add(
            web.Service(
                log=log, root=host.ROOT, routeList=routeList, api=api, port=host.PORT
            )
        ).add(
            PulseService(pulseStatus)
        ).run()
        log.info('%s %s', stopService.__class__.__name__, results or '')

def main(level=logger.INFO):
    global log
    logger.set(level=level)
    log = logger.get('web')
    try:
        asyncio.run(_amain())
    except KeyboardInterrupt:
        pass

def debug():
    main(level=logger.DEBUG)
    
main()
#debug()
