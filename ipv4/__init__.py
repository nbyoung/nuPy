import uasyncio as asyncio
import network
import time

class LocalAreaNetworkError(ValueError): pass

class LAN:

    async def _connect(self, lan, timeout_seconds=5):
        interval = 1
        lan.active(True)
        while True:
            if lan.isconnected():
                break
            if timeout_seconds <= 0:
                raise LocalAreaNetworkError(
                    'Timeout connecting network %s' % str(lan)
                )
            await asyncio.sleep(interval)
            timeout_seconds -= interval

    async def disconnect(self):
        network.LAN().disconnect()

    async def dhcp(self, timeout_seconds=5):
        await self._connect(network.LAN(), timeout_seconds=5)

    async def static(
            self, address, netmask, gateway, dns, timeout_seconds=5
    ):
        lan = network.LAN()
        lan.ifconfig((address, netmask, gateway, dns))
        await self._connect(lan, timeout_seconds=5)
