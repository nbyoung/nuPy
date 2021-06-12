
class Slave:

    def __init__(self, pduHandler, addresses=((0x00, 0xFF))):
        self._pduHandler = pduHandler
        self._addresses = addresses # TODO From configuration
                 
    @property
    def pduHandler(self): return self._pduHandler
                 
    @property
    def addresses(self): return self._addresses

class Handler:

    def __init__(self, aduClass, localSlave):
        # TODO Generalise to remote slaves as well as localSlave
        self._aduClass = aduClass
        self._localSlave = localSlave

    async def handle(self, bytes):
        adu = self._aduClass.fromBytes(bytes)
        return adu.reply(
            (
                await self._localSlave.pduHandler.handle(adu.pdu)
                if adu.address in self._localSlave.addresses
                # TODO Enable remote target access through configuration
                else adu.pdu.exception(
                        codes.Exception.GatewayTargetFailedToRespond
                )
            )
        ).toBytes()

    @property
    def size(self): return self._aduClass.MAX
