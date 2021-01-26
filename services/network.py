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

    async def loop(self, stopCallback):
        async with self._networkStatus.watcher as watcher:
            lan = ipv4.LAN()
            if watcher.get('is_dhcp'):
                await lan.dhcp()
            else:
                address = watcher.get('static.address')
                netmask = watcher.get('static.netmask')
                gateway = watcher.get('static.gateway')
                dns = watcher.get('static.dns')
                await lan.static(
                    address, netmask, gateway, dns=dns
                )
