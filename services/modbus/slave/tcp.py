try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
from collections import namedtuple
import logger
import select
import socket
import struct

from .. import codes
from ..pdu import PDU
import service

class ADU:

    _format     = '>HHHBB'
    MAX         = 260

    @staticmethod
    def fromBytes(bytes):
        size = struct.calcsize(ADU._format)
        transaction, protocol, length, slave, function = struct.unpack(
            ADU._format, bytes[:size]
        )
        octets = bytes[size:]
        return ADU(transaction, protocol, slave, function, octets)

    def __init__(self, transaction, protocol, slave, function, bytes):
        self._transaction = transaction
        self._protocol = protocol
        self._slave = slave
        self._function = function
        self._bytes = bytes

    @property
    def bytes(self):
        length = len(self._bytes) + struct.calcsize('BB')
        return struct.pack(
            ADU._format,
            self._transaction, self._protocol, length, self._slave, 
            self._function
            ) + self._bytes

    @property
    def slave(self): return self._slave

    @property
    def pdu(self): return PDU(self._function, self._bytes)

    def reply(self, pdu):
        return self.__class__(
            self._transaction, self._protocol, self._slave,
            pdu.functionCode, pdu.bytes
            )


class Slave:

    def __init__(self, pduHandler, addresses=((0x00, 0xFF))):
        self._pduHandler = pduHandler
        self._addresses = addresses # TODO From configuration
                 
    @property
    def pduHandler(self): return self._pduHandler
                 
    @property
    def addresses(self): return self._addresses

class Handler:

    size = ADU.MAX

    def __init__(self, localSlave=None):
        # TODO Accept remote device addresses
        self._localSlave = localSlave

    async def handle(self, bytes):
        adu = ADU.fromBytes(bytes)
        return adu.reply(
            (
                await self._localSlave.pduHandler.handle(adu.pdu)
                if adu.slave in self._localSlave.addresses
                # TODO Enable remote target access through configuration
                else adu.pdu.exception(
                        codes.Exception.GatewayTargetFailedToRespond
                )
            )
        ).bytes
        
Client = namedtuple('Client', ('socket', 'address'))

class ServiceError(OSError): pass

class Service(service.Service):

    _log = logger.get()

    # TODO busStatus: Control en/disable
    # TODO clientStatus: Report address, bytes received
    def __init__(self, handler, dataStatus, port=502, ip='0.0.0.0'):
        self._handler = handler
        self._dataStatus = dataStatus
        self._value = 0
        self._address = socket.getaddrinfo(ip, port)[0][-1]
        self._serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._serverSocket.bind(self._address)
        self._serverSocket.listen(0)
        self._poll = select.poll()
        self._poll.register(self._serverSocket, select.POLLIN)
    
    async def loop(self, stopCallback):
        ready = self._poll.poll(0)
        if 0 < len(ready):
            (_, mask) = ready[0]
            if mask != select.POLLIN:
                raise ServiceError('select.poll() 0x%x' % mask)
            client = Client(*self._serverSocket.accept())
            address = (
                # b'\x02\x00\x89L\x7f\x00\x00\X01'
                # b'\x02\x00\xd2<\xc0\xa8\x01\x0b\x00\x00\x00\x00\x00\x00\x00\x00'
                (
                    ".".join(
                        [str(byte[0])
                         for byte in struct.unpack('ssss', client.address[4:8])]
                    ),
                    struct.unpack('H', client.address[2:4])[0]
                ) if type(client.address) is bytearray
                else client.address
            )
            Service._log.debug(
                '%s.%s connection from %s via %s' % (
                    __name__, self.__class__.__name__, address, client.socket
                )
            )
            while True:
                await asyncio.sleep(0)
                bytes = client.socket.recv(self._handler.size)
                if bytes:
                    if not client.socket.send(await self._handler.handle(bytes)):
                        break
                else:
                    break
            client.socket.close()
        await asyncio.sleep(0)

    async def onStop(self):
        self._poll.unregister(self._serverSocket)
        self._serverSocket.close()
