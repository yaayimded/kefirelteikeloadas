import socket
import struct
import sys

packer = struct.Struct("i i c")                    # egyelore csak a 'Hello server' uzenet
server_addr = (sys.argv[1], int(sys.argv[2]))
a, op, b = int(sys.argv[3]), sys.argv[4], int(sys.argv[5])   # pl. python client.py localhost 10000
op = "*" if op == "x" else op
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect(server_addr)
    client.sendall(packer.pack(a, b, op.encode()))
    result, _, _ = packer.unpack(client.recv(256))
    print(f"Received: {result}")
