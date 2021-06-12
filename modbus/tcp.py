try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
from collections import namedtuple
import logger
import select
import socket
import struct

import service

from . import _adu

class ADU(_adu._ADU):

    _format     = '>HHHBB'
    MAX         = 260

    @staticmethod
    def fromBytes(bytes_):
        size = struct.calcsize(ADU._format)
        transaction, protocol, length, address, function = struct.unpack(
            ADU._format, bytes_[:size]
        )
        return ADU(transaction, protocol, address, function, bytes_[size:])

    def __init__(self, transaction, protocol, address, function, pduBytes):
        super().__init__(address, function, pduBytes)
        self._transaction = transaction
        self._protocol = protocol

    def toBytes(self):
        length = len(self._pduBytes) + struct.calcsize('BB')
        return struct.pack(
            ADU._format,
            self._transaction, self._protocol, length, self._address, 
            self._function
            ) + self._pduBytes

    def reply(self, pdu):
        return self.__class__(
            self._transaction, self._protocol, self._address,
            pdu.functionCode, pdu.bytes
        )
        
Client = namedtuple('Client', ('socket', 'address'))

class ServiceError(OSError): pass

class SlaveService(service.Service):

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
    
    async def onLoop(self, stopCallback):
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
            SlaveService._log.debug(
                '%s.%s connection from %s via %s' % (
                    __name__, self.__class__.__name__, address, client.socket
                )
            )
            while True:
                await asyncio.sleep(0)
                bytes = client.socket.recv(self._handler.size)
                if bytes:
                    try:
                        if not client.socket.send(await self._handler.handle(bytes)):
                            break
                    except CRCError as error:
                        SlaveService._log.warning(str(error)) # TODO Handle CRC error
                else:
                    break
            client.socket.close()
        await asyncio.sleep(0)

    async def onStop(self):
        self._poll.unregister(self._serverSocket)
        self._serverSocket.close()
