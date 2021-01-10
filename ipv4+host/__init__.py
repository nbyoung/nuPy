import socket

class _EndPoint:

    @property
    def family(self): return socket.AF_INET

    @property
    def type(self): return self._type

    @property
    def address(self): return self._address

    @property
    def port(self): return self._port

    def __init__(self, type, address, port):
        self._type = type
        self._address = address
        self._port = port

class UDPEndPoint(_EndPoint):

    def __init__(self, address, port):
        super().__init__(socket.SOCK_DGRAM, address, port)
    

class TCPEndPoint(_EndPoint):

    def __init__(self, address, port):
        super().__init__(socket.SOCK_STREAM, address, port)

class LocalAreaNetworkError(ValueError): pass

class LAN:

    address = '192.168.1.11'
    netmask = '255.255.255.0'
    gateway = '192.168.1.1'
    dns = '8.8.8.8'

    def _connect(self, timeout_seconds, dns=None, test=lambda _: True):
        tcpEndPoint = TCPEndPoint(dns or LAN.dns, 53)
        client = socket.socket(tcpEndPoint.family, tcpEndPoint.type)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client.settimeout(timeout_seconds)
        client.connect(socket.getaddrinfo(tcpEndPoint.address, tcpEndPoint.port)[0][-1])
        test(client)
        client.close()

    async def disconnect(self):
        pass

    async def dhcp(self, timeout_seconds=3):
        self._connect(timeout_seconds)

    async def static(
            self, address, netmask, gateway, dns, timeout_seconds=3
    ):
        def test(client):
            try:
                # Required for ports/unix running on Linux
                # Micropython socket does not implement getsockname()
                client_address = client.getsockname()[0]
                if client_address != address:
                    raise LocalAreaNetworkError(
                        'LAN.static() address %s different from %s'
                        % (address, client_address)
                    )
            except AttributeError:
                pass
        self._connect(timeout_seconds, dns, test)
