import select
import socket
import struct
import time
import sys

ADDR = ("localhost", int(sys.argv[1]))
request_packer = struct.Struct("2s i i")
reply_packer = struct.Struct("i")
ids = {}

def select_server():
    """Egyszerre több klienssel foglalkozik: a select megmondja, melyik socketen van teendő."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(ADDR)
        server.listen(5)
        print("Select szerver fut:", ADDR)
        inputs = [server]
        while True:
            try:
                readables, _, _ = select.select(inputs, [], [], 1.0)
                for s in readables:
                    if s is server:  # új kliens csatlakozik
                        client, addr = server.accept()
                        inputs.append(client)
                        print("Új kliens:", addr)
                        continue
                    msg = s.recv(12)  
                    if not msg:
                        print("Egy kliens bontott")
                        s.close()
                        inputs.remove(s)  
                        continue
                    com, id, amount = request_packer.unpack(msg)
                    if id not in ids:
                        ids[id] = 0
                    if (com == b"BE"):
                        ids[id] = ids.get(id)+amount
                    elif(com == b"KI"):
                        ids[id] = ids.get(id)-amount
                    else:
                        s.close()
                        inputs.remove(s)
                        continue   
                    total = reply_packer.pack(ids.get(id))
                    s.sendall(total)
            except Exception:
                print("Client broke the connection.")
                inputs.remove(s)


if __name__ == "__main__":
    select_server()
