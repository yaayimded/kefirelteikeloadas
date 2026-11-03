import socket
import struct
import sys

packer = struct.Struct("6s i i")                    # egyelore csak a 'Hello server' uzenet
packer2 = struct.Struct("6s 10s i")                    # egyelore csak a 'Hello server' uzenet
packer3 = struct.Struct("c 10s")                    # egyelore csak a 'Hello server' uzenet
packer4 = struct.Struct("12s")                    # egyelore csak a 'Hello server' uzenet                  # egyelore csak a 'Hello server' uzenet
server_addr = (sys.argv[1], int(sys.argv[2]))
neptune = sys.argv[3]

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect(server_addr)
    start = 50
    half = 25
    result = ""
    counter = 1
    code = ''
    
    while(result != b'='):
        client.sendall(packer.pack(neptune.encode(), start, counter))
        data = client.recv(packer3.size)
        result, code = packer3.unpack(data)
        if result == b'>':
            start += half
            half = half//2
        elif result == b'<':
            start -= half
            half = half//2
        counter += 1
    client.sendall(packer2.pack(neptune.encode(), code, counter))
    data = client.recv(packer4.size)
    code = packer4.unpack(data)
