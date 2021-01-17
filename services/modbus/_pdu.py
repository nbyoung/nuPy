import struct

from . import codes
from . import _data

class PDU:

    @property
    def functionCode(self): return self._functionCode

    @property
    def bytes(self): return self._bytes
    
    def __init__(self, functionCode, bytes=b''):
        self._functionCode = functionCode
        self._bytes = bytes

    def exception(self, code): # Move to Transcoder
        return 

class IllegalFunction(Exception): code = codes.Exception.IllegalFunction

class Handler:

    @staticmethod
    def _exceptionPDU(exceptionCode, functionCode):
        return PDU(
            functionCode | codes.Exception.Mask,
            struct.pack('>B', exceptionCode)
        )

    def __init__(self, dataModel, logCallback):
        self._dataModel = dataModel
        self._logCallback = logCallback

    async def handle(self, pdu):
        try:
            code = pdu.functionCode
            if code == codes.Function.ReadMultipleHoldingRegisters:
                fromRegion = _data.Region(
                    *struct.unpack('>HH', pdu.bytes), max=125
                )
                self._dataModel.holdingBlock.validRegion(fromRegion)
                bytes = await self.ReadMultipleHoldingRegisters(
                    self._dataModel, fromRegion
                )
            elif code == codes.Function.WriteSingleHoldingRegister:
                format = '>HH'
                toAddress, value = struct.unpack(
                    format, pdu.bytes[:struct.calcsize(format)]
                )
                self._dataModel.holdingBlock.validRegion(
                    _data.Region(toAddress, 1, 1)
                )
                bytes = await self.WriteSingleHoldingRegister(
                    self._dataModel, toAddress, value
                )
            elif code == codes.Function.WriteMultipleHoldingRegisters:
                format = '>HHB'
                toAddress, toCount, byteCount = struct.unpack(
                    format, pdu.bytes[:struct.calcsize(format)]
                )
                toRegion = _data.Region(toAddress, toCount, max=0x7B)
                self._dataModel.holdingBlock.validRegion(toRegion)
                values = tuple(struct.unpack(
                    '>%dH' % toCount, pdu.bytes[struct.calcsize(format):]
                ))
                bytes = await self.WriteMultipleHoldingRegisters(
                    self._dataModel, toRegion, values
                )
            elif code == codes.Function.ReadWriteMultipleRegisters:
                format = '>HHHHB'
                (
                    fromAddress, fromCount, toAddress, toCount, byteCount
                ) = struct.unpack(format, pdu.bytes[:struct.calcsize(format)])
                fromRegion = Region(fromAddress, fromCount, max=0x7D)
                self._dataModel.holdingBlock.validRegion(fromRegion)
                toRegion = _data.Region(toAddress, toCount, max=0x79)
                self._dataModel.holdingBlock.validRegion(toRegion)
                values = tuple(struct.unpack(
                    '>%dH' % toCount, pdu.bytes[struct.calcsize(format):]
                ))
                bytes = await self.ReadWriteMultipleRegisters(
                    self._dataModel, fromRegion, toRegion, values
                )
            else:
                raise IllegalFunction()
            return PDU(code, bytes)
        except IllegalFunction as exception:
            self._logCallback(
                'Function code=%d %s not implemented',
                pdu.functionCode, str(exception)
            )
            return Handler._exceptionPDU(pdu.functionCode, exception.code)
        except _data.IllegalDataAddress as exception:
            self._logCallback(
                'Function code=%d %s', pdu.functionCode, str(exception)
            )
            return Handler._exceptionPDU(pdu.functionCode, exception.code)

    async def ReadMultipleHoldingRegisters(self, dataModel, fromRegion):
        raise IllegalFunction("ReadMultipleHoldingRegisters")

    async def WriteSingleHoldingRegister(self, dataModel, toAddress, value):
        raise IllegalFunction("WriteSingleHoldingRegister")

    async def WriteMultipleHoldingRegisters(self, dataModel, toRegion, values):
        raise IllegalFunction("WriteMultipleHoldingRegisters")

    async def ReadWriteMultipleHoldingRegisters(
            self, dataModel, fromRegion, toRegion, values
    ):
        raise IllegalFunction("ReadWriteMultipleHoldingRegisters")
