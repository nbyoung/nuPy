import struct

from . import codes
from . import _data

class PDU:

    @property
    def functionCode(self): return self._functionCode

    @property
    def bytes(self): return self._bytes
    
    def __init__(self, functionCode, bytes_=b''):
        self._functionCode = functionCode
        self._bytes = bytes_

    def exception(self, code):
        return PDU(self._functionCode + codes.Exception.Mask, struct.pack('>B', code))

class IllegalFunction(Exception): code = codes.Exception.IllegalFunction

class RequestHandler:

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
                bytes_ = await self.ReadMultipleHoldingRegisters(fromRegion)
            elif code == codes.Function.WriteSingleHoldingRegister:
                format = '>HH'
                toAddress, value = struct.unpack(
                    format, pdu.bytes[:struct.calcsize(format)]
                )
                self._dataModel.holdingBlock.validRegion(
                    _data.Region(toAddress, 1, 1)
                )
                bytes_ = await self.WriteSingleHoldingRegister(toAddress, value)
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
                bytes_ = await self.WriteMultipleHoldingRegisters(toRegion, values)
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
                bytes_ = await self.ReadWriteMultipleRegisters(
                    fromRegion, toRegion, values
                )
            else:
                raise IllegalFunction()
            return PDU(code, bytes_)
        except IllegalFunction as exception:
            self._logCallback(
                'Function code=%d %s not implemented',
                pdu.functionCode, str(exception)
            )
            return RequestHandler._exceptionPDU(pdu.functionCode, exception.code)
        except _data.IllegalDataAddress as exception:
            self._logCallback(
                'Function code=%d %s', pdu.functionCode, str(exception)
            )
            return RequestHandler._exceptionPDU(pdu.functionCode, exception.code)

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
