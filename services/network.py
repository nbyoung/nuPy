import configuration
import ipv4
import static
import service

JSON = """{
    "is_dhcp":      true,
    "static": {
        "address":  "%s",
        "netmask":  "%s",
        "gateway":  "%s",
        "dns":      "%s"
    }
}""" % (
    static.IPv4.address, static.IPv4.netmask, static.IPv4.gateway, static.IPv4.dns,
)

def Status(path):
    return configuration.Status(configuration.JSONStore(path, JSON))

class Service(service.Service):

    def __init__(self, networkStatus):
        self._networkStatus = networkStatus

    async def _set(self, getter):
        lan = ipv4.LAN()
        if getter.get('is_dhcp'):
            await lan.dhcp()
        else:
            address = getter.get('static.address')
            netmask = getter.get('static.netmask')
            gateway = getter.get('static.gateway')
            dns = getter.get('static.dns')
            await lan.static(
                address, netmask, gateway, dns=dns
            )

    async def start(self):
        async with self._networkStatus.getter as getter:
            await self._set(getter)

    async def loop(self, stopCallback):
        async with self._networkStatus.watcher as getter:
            await self._set(getter)
