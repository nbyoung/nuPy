import struct

from .pdu import PDU

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
