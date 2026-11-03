import socket
import struct
import sys

query = struct.Struct("!7H B6s B6s B 2H")                # egyelore csak a 'Hello server' uzenet
reply = struct.Struct("!7H B6s B6s B 2H HHHIH 4s")
server_addr = (sys.argv[1], int(sys.argv[2]))
neptun = sys.argv[3]   # pl. python client.py localhost 10000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect(server_addr)
    client.sendall(query.pack(query.size - 2, 1234, 0x0100, 1, 0, 0, 0, 6, neptun.encode(), 6, b"telkom", 0, 1, 1))
    data = client.recv(reply.size)
    result = reply.unpack(data)[19]
    print(socket.inet_ntoa(result))
