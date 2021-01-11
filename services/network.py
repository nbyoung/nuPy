import configuration
import ipv4
import service

JSON = """{
    "is_dhcp":      true,
    "static": {
        "address":  "%s",
        "netmask":  "%s",
        "gateway":  "%s",
        "dns":      "%s"
    }
}""" % (ipv4.LAN.address, ipv4.LAN.netmask, ipv4.LAN.gateway, ipv4.LAN.dns, )

def Status(path):
    return configuration.Status(configuration.JSONStore(path, JSON))

class Service(service.Service):

    def __init__(self, runner, networkStatus):
        super().__init__(runner)
        self._networkStatus = networkStatus

    async def loop(self, stopCallback):
        async with self._networkStatus.watcher as watcher:
            lan = ipv4.LAN()
            if watcher.get('is_dhcp'):
                await lan.dhcp()
                print('lan.dhcp')
            else:
                address = watcher.get('static.address')
                netmask = watcher.get('static.netmask')
                gateway = watcher.get('static.gateway')
                dns = watcher.get('static.dns')
                await lan.static(
                    address, netmask, gateway, dns=dns
                )
                print('lan.static')
