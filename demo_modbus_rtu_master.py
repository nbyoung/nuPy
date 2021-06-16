# TODO Responses

from modbus import pdu, rtu

def main():
    adu = pdu.Request(
        lambda functionCode, pduBytes: rtu.ADU(0, functionCode, pduBytes)
    ).ReadMultipleHoldingRegisters(0, 1)
    print(adu.toBytes())
    
main()
