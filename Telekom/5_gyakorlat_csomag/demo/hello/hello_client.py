import socket
import sys

server_addr = ("localhost", int(sys.argv[1]))   # pl. python hello_client.py 10000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect(server_addr)
    client.sendall("Hello server".encode())
    data = client.recv(16)
    print("Received:", data.decode())
