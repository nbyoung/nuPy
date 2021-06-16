try:
    import usocket as socket
except ImportError:
    import socket

from modbus import pdu, tcp

# TODO Responses

PROTOCOL = 0

def _transaction():
    t = 0
    while True:
        yield t
        t = (t + 1) % 2**16

TRANSACTION = _transaction()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("192.168.1.11", 502))

    adu = pdu.Request(
        lambda functionCode, pduBytes:
        tcp.ADU(next(TRANSACTION), PROTOCOL, 255, functionCode, pduBytes)
    ).ReadMultipleHoldingRegisters(0, 1)
    s.sendall(adu.toBytes())
    print(adu.toBytes())
    print(s.recv(256))
    s.close()
    
main()
