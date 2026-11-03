import socket
import struct
import sys

equation = {
    b'+': lambda a, b: a+b,
    b'-': lambda a, b: a-b,
    b'*': lambda a, b: a*b,
    b'/': lambda a, b: a//b
}


packer = struct.Struct("i i c")                    # egyelore csak a 'Hello server' uzenet
server_addr = ("localhost", int(sys.argv[1]))   # pl. python server.py 10000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(server_addr)
    sock.listen(1)
    sock.settimeout(1.0)                         # Windowson a Ctrl+C csak igy szakitja meg az accept-et

    try:
        while True:
            try:
                client, client_addr = sock.accept()
                print(f"Connected: {client_addr[0]}:{client_addr[1]}")
                with client:
                    a, b, op = packer.unpack(client.recv(packer.size))                        # a kliens meg nem kuldi az azonositojat
                    result = equation[op](a, b)
                    client.sendall(packer.pack(result, 0, b'k'))
            except TimeoutError:                 # 1 mp alatt nem jott kliens: varunk tovabb
                pass
    except KeyboardInterrupt:
        print("Server stopped")
