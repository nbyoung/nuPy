import struct

from .. import adu

class ADU(adu.ADU):

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
