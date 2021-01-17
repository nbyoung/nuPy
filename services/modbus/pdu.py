import struct

from . import _pdu

class PDU(_pdu.PDU): pass

class Handler(_pdu.Handler):

    def __init__(self, dataModel, logCallback=lambda _: None):
        super().__init__(dataModel, logCallback)

    async def ReadMultipleHoldingRegisters(self, dataModel, fromRegion):
        async with dataModel.status.getter as getter:
            return struct.pack(
                '>B%dH' % fromRegion.count,
                fromRegion.count * 2,
                *[dataModel.holdingRead(getter, fromRegion.address + i)
                  for i in range(fromRegion.count)]
            )

    async def WriteSingleHoldingRegister(
            self, dataModel, toAddress, value
    ):
        async with dataModel.status.setter as setter:
            dataModel.holdingWrite(setter, toAddress, value)
            return struct.pack('>HH', toAddress, value)

    async def WriteMultipleHoldingRegisters(
            self, dataModel, toRegion, values
    ):
        async with dataModel.status.setter as setter:
            for i in range(toRegion.count):
                dataModel.holdingWrite(setter, toRegion.address + i, values[i])
            return struct.pack('>HH', toRegion.address, toRegion.count)

    async def ReadWriteMultipleRegisters(
            self, dataModel, fromRegion, toRegion, values
    ):
        async with dataModel.status.setter as setter:
            for i in range(toRegion.count):
                dataModel.holdingWrite(setter, toRegion.address + i, values[i])
            return struct.pack(
                '>B%dH' % fromRegion.count,
                fromRegion.count * 2,
                *[dataModel.holdingRead(setter, fromRegion.address + i)
                  for i in range(fromRegion.count)]
            )
