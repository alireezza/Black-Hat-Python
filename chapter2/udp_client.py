#!/usr/bin/env python3 
import socket 

target_host = "127.0.0.1"
target_port = 9999 

# 1. Create a socket object
# SOCK_DGRAM = UDP (User Datagram Protocol)
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 2. send some data 
# Because UDP is connectionless, we use sindto() and pass the target host and port as a tuple.
client.sendto(b"AAABBBCCC", (target_host, target_port))

# 3. Receive some data from the server
# recvfrom() returns a tuple containing the data and the address of the sender.
data, addr = client.recvfrom(4096)

print(data.decode())
client.close() 
