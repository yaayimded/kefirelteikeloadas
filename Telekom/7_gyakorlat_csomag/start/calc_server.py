import socket
import struct
import sys

op_packer = struct.Struct("i i c")
answer_packer = struct.Struct("i")
ops = {
    b"+": lambda a, b: a + b,
    b"-": lambda a, b: a - b,
    b"*": lambda a, b: a * b,
    b"/": lambda a, b: a // b,
}
server_addr = ("localhost", int(sys.argv[1]))  # pl. python calc_server.py 10000

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.bind(server_addr)
    sock.settimeout(1.0)  # Windowson a Ctrl+C csak igy szakitja meg az accept-et
    try:
        while True:
            try:
                data, client = sock.recvfrom(1024)
                a, b, op = op_packer.unpack(data)
                result = ops[op](a, b)
                data = sock.sendto(answer_packer.pack(result), client)
            except TimeoutError:  # 1 mp alatt nem jott kliens: varunk tovabb
                pass
    except KeyboardInterrupt:
        print("Server stopped")
