import select
import socket
import struct
import sys


DESTINATION1_ADDR = ("localhost", int(sys.argv[1]))
DESTINATION2_ADDR = ("localhost", int(sys.argv[2]))
GATEWAY_ADDR = ("localhost", int(sys.argv[3]))  # a square_gateway.py


operand_packer = struct.Struct("i i c")  # a klienstol: nev es szam
two_nums = struct.Struct("i i")
answer_packer = struct.Struct("i")  # a szervernek: csak a szam; a szerver valasza is (i)



def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            return b""
        data += chunk
    return data


def tcp_proxy():
    """A kliensek felé szerver (select), a szerver felé kliens: egyetlen, állandó kapcsolattal."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as destination1, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as destination2, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as gateway:
        destination2.connect(DESTINATION2_ADDR)
        gateway.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        gateway.bind(GATEWAY_ADDR)
        gateway.listen(5)
        print("Proxy is running:", GATEWAY_ADDR, "->", DESTINATION1_ADDR, DESTINATION2_ADDR)
        inputs = [gateway]  # a destination NEM kerul ide: a valaszt rogton megvarjuk rajta
        while True:
            readables, _, _ = select.select(inputs, [], [], 1.0)
            for s in readables:
                if s is gateway:
                    client, addr = gateway.accept()
                    print(f"New client: {addr[0]}:{addr[1]}")
                    inputs.append(client)
                    continue
                msg = recv_exact(s, operand_packer.size)
                if not msg:
                    inputs.remove(s)
                    s.close()
                    continue
                # atcsomagolas: a szerver csak a szamot kapja
                a, b, op = operand_packer.unpack(msg)
                if op == b"*":
                    destination2.sendall(two_nums.pack(a, b))
                    result = recv_exact(destination2, answer_packer.size)
                    s.sendall(result)
                elif op == b"+":
                    destination1.sendto(two_nums.pack(a, b), DESTINATION1_ADDR)
                    result, _ = destination1.recvfrom(1024)
                    s.sendall(result)
                else:
                    s.close()
                    inputs.remove(s)


if __name__ == "__main__":
    try:
        tcp_proxy()
    except KeyboardInterrupt:
        print("Proxy stopped")
