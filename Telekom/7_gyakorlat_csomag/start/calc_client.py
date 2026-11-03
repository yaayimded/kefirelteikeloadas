import socket
import struct
import sys

operand_packer = struct.Struct("i i c")  # ket szam es a muveleti jel
answer_packer = struct.Struct("i")
# pl. python calc_client.py localhost 10000 6 x 7   (a szorzas jele itt x, mert a * a shellben mast jelent)
port, a, op, b = (
    int(sys.argv[1]),
    int(sys.argv[2]),
    sys.argv[3],
    int(sys.argv[4]),
)
op = "*" if op == "x" else op

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect(("localhost", port))
    client.sendall(operand_packer.pack(a, b, op.encode()))
    result = answer_packer.unpack(client.recv(answer_packer.size))
    print(f"{a} {op} {b} = {result[0]}")
