import select
import socket
import struct
import sys

PROXY_ADDR = ("localhost", int(sys.argv[1]))
SERVER_ADDR = ("localhost", int(sys.argv[2]))  # a square_server.py

operand_packer = struct.Struct("i i c")  # a klienstol: nev es szam
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
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as backend, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(PROXY_ADDR)
        server.listen(5)
        print("Proxy is running:", PROXY_ADDR, "->", SERVER_ADDR)
        inputs = [server]  # a backend NEM kerul ide: a valaszt rogton megvarjuk rajta
        while True:
            readables, _, _ = select.select(inputs, [], [], 1.0)
            for s in readables:
                if s is server:
                    client, addr = server.accept()
                    print(f"New client: {addr[0]}:{addr[1]}")
                    inputs.append(client)
                    continue
                msg = recv_exact(s, operand_packer.size)
                if not msg:
                    inputs.remove(s)
                    s.close()
                    continue
                # atcsomagolas: a szerver csak a szamot kapja
                backend.sendto(msg, SERVER_ADDR)
                msg, _ = backend.recvfrom(1024)
                s.sendall(msg)


if __name__ == "__main__":
    try:
        tcp_proxy()
    except KeyboardInterrupt:
        print("Proxy stopped")
