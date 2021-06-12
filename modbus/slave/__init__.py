
class Handler:

    def __init__(self, aduClass, localSlave=None):
        # TODO Accept remote device addresses
        self._aduClass = aduClass
        self._localSlave = localSlave

    async def handle(self, bytes):
        adu = self._aduClass.fromBytes(bytes)
        return adu.reply(
            (
                await self._localSlave.pduHandler.handle(adu.pdu)
                if adu.slave in self._localSlave.addresses
                # TODO Enable remote target access through configuration
                else adu.pdu.exception(
                        codes.Exception.GatewayTargetFailedToRespond
                )
            )
        ).toBytes()

    @property
    def size(self): return self._aduClass.MAX
