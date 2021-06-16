# warning:      Untested.

import struct

from . import adu, pdu

class ADU(adu.ADU):

    _head       = '>BB'
    _crc        = '>H'
    MAX         = 256

    @staticmethod
    def fromBytes(bytes_):
        headSize = struct.calcsize(ADU._head)
        address, function = struct.unpack(ADU._head, bytes_[:headSize])
        crcSize = struct.calcsize(ADU._crc)
        crc, = struct.unpack(ADU._crc, bytes_[-crcSize:])
        pduBytes = bytes_[headSize:-crcSize:]
        if False: # TODO: CRC check
            raise modbus.CRCError(
                'CRC error: address=%d, function=%d' % (address, function)
            )
        return ADU(address, function, pduBytes)

    def __init__(self, address, function, pduBytes):
        self._address = address
        self._function = function
        self._pduBytes = pduBytes

    @property
    def address(self): return self._address

    @property
    def pdu(self): return pdu.PDU(self._function, self._pduBytes)

    def toBytes(self):
        length = len(self._pduBytes) + struct.calcsize('BB')
        crc = 0 # TODO crc(address, function, pduBytes)
        return (
            struct.pack(ADU._head, self._address, self._function)
            + self._pduBytes
            + struct.pack(ADU._crc, crc)
        )

    def reply(self, pdu):
        return self.__class__(self._address, pdu.functionCode, pdu.bytes)
