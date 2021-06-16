
from .pdu import PDU

class ADU:

    def __init__(self, address, function, pduBytes):
        self._address = address
        self._function = function
        self._pduBytes = pduBytes

    @property
    def address(self): return self._address

    @property
    def pdu(self): return PDU(self._function, self._pduBytes)
