try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
import configuration
import logger
import service
import tmp

class PendulumService(service.Service):

    def __init__(self, runner, anchorStatus, period=1.0):
        super().__init__(runner)
        self._anchorStatus = anchorStatus
        self._period = period

    async def loop(self, stopCallback):
        async with self._anchorStatus.setter as setter:
            self._value = await setter.get('pallet')
            setter.set('pallet', not self._value)
        await asyncio.sleep(self._period / 2)

    async def onStop(self):
        await asyncio.sleep(self._period)
        return self._value

class ClockService(service.Service):

    def __init__(self, runner, anchorStatus, clockStatus, haltSecond=60):
        super().__init__(runner)
        self._anchorStatus = anchorStatus
        self._clockStatus = clockStatus
        self._haltSecond = haltSecond

    async def loop(self, stopCallback):
        async with self._anchorStatus.watcher as watcher:
            if await watcher.get('pallet'):
                async with self._clockStatus.setter as setter:
                    second = await setter.get('second') + 1
                    minute = await setter.get('minute') + second // 60
                    hour = await setter.get('hour') + minute // 60
                    second = second % 60
                    setter.set('second', second)
                    minute = minute % 60
                    setter.set('minute', minute)
                    hour = hour % 24
                    setter.set('hour', hour)
                self._time = '%02dh%02dm%02ds' % (hour, minute, second)
                log.info(self._time)
                if not second % self._haltSecond:
                    stopCallback()

    async def onStop(self):
        return self._time

async def _amain():
    anchorJSON = """
{
    "pallet":   false
}
    """
    clockJSON = """
{
    "second":   0,
    "minute":   0,
    "hour":     0
}
    """
    anchorStatus = configuration.Status(configuration.JSONStore(None, anchorJSON))
    with tmp.Path('clock.json') as clockPath:
        clockStatus = configuration.Status(configuration.JSONStore(clockPath, clockJSON))
        stopService, results = await service.Runner(
        ).add(
            PendulumService, anchorStatus
        ).add(
            ClockService, anchorStatus, clockStatus, haltSecond=3
        ).run()
        log.info('%s %s', stopService.__class__.__name__, results)

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
