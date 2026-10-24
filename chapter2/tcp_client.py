#!/usr/bin/env python3 
# The Shebang tells the system to use Python 3 to execute this script.
import socket # Import the socket module to create a TCP client.

# Define the target host and port to connect to 
target_host = "www.google.com"
target_port = 80
# 1. Create a socket object 
# AF_INET = Ipv4 (Standard for Internet Protocol v4 addresses)
# SOCK_STREAM = TCP (Transmission Control Protocol)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2. Connect the client to the target host and port 
# We pass the target host and port as a tuple to the connect() method.
client.connect((target_host, target_port))
# 3. Send some data to the server 
# We send an HTTP GET request to the server. The request is a string that we encode to bytes.
client.send(b'GET / HTTP/1.1\r\nHost: google.com\r\n\r\n')

# 4. Receive some data from the server 
# 4096 is the buffer size, which means we will receive up to 4096 bytes of data from the server. 
response = client.recv(4096) 

# 5 . Print the response from the server
# .decode() turns the raw bytes back into redable text 
print(response.decode()) 

# 6. Close the client socket and
client.close()