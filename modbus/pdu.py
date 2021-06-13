import struct

from . import _pdu

class PDU(_pdu.PDU): pass

class RequestHandler(_pdu.RequestHandler):

    def __init__(self, dataModel, logCallback=lambda _: None):
        super().__init__(dataModel, logCallback)

    async def ReadMultipleHoldingRegisters(self, fromRegion):
        async with self._dataModel.status.getter as getter:
            return struct.pack(
                '>B%dH' % fromRegion.count,
                fromRegion.count * 2,
                *[self._dataModel.holdingRead(getter, fromRegion.address + i)
                  for i in range(fromRegion.count)]
            )

    async def WriteSingleHoldingRegister(
            self, toAddress, value
    ):
        async with self._dataModel.status.setter as setter:
            self._dataModel.holdingWrite(setter, toAddress, value)
            return struct.pack('>HH', toAddress, value)

    async def WriteMultipleHoldingRegisters(
            self, toRegion, values
    ):
        async with self._dataModel.status.setter as setter:
            for i in range(toRegion.count):
                self._dataModel.holdingWrite(setter, toRegion.address + i, values[i])
            return struct.pack('>HH', toRegion.address, toRegion.count)

    async def ReadWriteMultipleRegisters(
            self, fromRegion, toRegion, values
    ):
        async with self._dataModel.status.setter as setter:
            for i in range(toRegion.count):
                self._dataModel.holdingWrite(setter, toRegion.address + i, values[i])
            return struct.pack(
                '>B%dH' % fromRegion.count,
                fromRegion.count * 2,
                *[self._dataModel.holdingRead(setter, fromRegion.address + i)
                  for i in range(fromRegion.count)]
            )
