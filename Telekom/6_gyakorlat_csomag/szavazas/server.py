import select
import socket
import struct
import sys

ADDR = ("localhost", int(sys.argv[1]))
request_packer = struct.Struct("4s i")
reply_packer = struct.Struct("i")
votes = {}

def recv_exact(sock, size):
    """Addig olvas, amíg pontosan size byte meg nem érkezik (vagy a másik oldal bont)."""
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            return b""
        data += chunk
    return data

def getnumofvotes(num):
    counter = 0
    for i in votes:
        if(votes[i] == num):
            counter+=1
    return counter

def select_server():
    """Egyszerre több klienssel foglalkozik: a select megmondja, melyik socketen van teendő."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(ADDR)
        server.listen(20)
        print("Select szerver fut:", ADDR)
        inputs = [server]
        while True:
            try:
                readables, _, _ = select.select(inputs, [], [], 1.0)
                for s in readables:
                    if s is server:  # új kliens csatlakozik
                        client, addr = server.accept()
                        inputs.append(client)
                        #print("Új kliens:", addr)
                        continue
                    msg = recv_exact(s, request_packer.size)
                    if not msg:
                        print("Egy kliens bontott")
                        s.close()
                        inputs.remove(s)
                        continue
                    com, num = request_packer.unpack(msg)
                    if(num > 5 or num < 0):
                        s.sendall(reply_packer.pack(-2))
                        s.close()
                        inputs.remove(s)
                        continue
                    adr = s.getpeername()
                    if (com == b"VOTE" and adr not in votes):
                        votes[adr] = num
                        s.sendall(reply_packer.pack(getnumofvotes(num)))
                    elif(com == b"VOTE" and adr in votes):
                        s.sendall(reply_packer.pack((-1)))
                    elif(com == b"UNDO" and adr in votes):
                        num = votes[adr]
                        votes.pop(adr)
                        s.sendall(reply_packer.pack(getnumofvotes(num)))
                    elif(com == b"UNDO" and adr not in votes):
                        s.sendall(reply_packer.pack((-1)))
                    elif com == b"STAT":
                        if(num == 0):
                            counter = 0
                            for i in range(1,6):
                                counter += getnumofvotes(i)
                            s.sendall(reply_packer.pack(counter))
                        else:
                            s.sendall(reply_packer.pack(getnumofvotes(num)))
                    else:
                        s.sendall(reply_packer.pack(-2))
            except Exception:
                print("Client broke the connection.")
                inputs.remove(s)


if __name__ == "__main__":
    select_server()