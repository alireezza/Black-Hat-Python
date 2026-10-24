#!/usr/bin/env python3
import socket 
import threading 
# "0.0.0.0" means listen on all available network interfaces(Wi-Fi, Ethernet, etc.)
bind_ip = "0.0.0.0"
bind_port = 9998

def hanle_client(client_socket):
    # Print out what the client sends 
    request = client_socket.recv(1024)
    print(f"[*] Received: {request.decode()}")
    
    # Send back a packet 
    client_socket.send(b"ACK!")
    
    # Close the connection
    client_socket.close()
def main():
    # Create a socket object 
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket to the IP and port 
    server.bind((bind_ip, bind_port))
    
    # Start listening for incoming connections 
    server.listen(5)
    print(f"[*] Listening on {bind_ip}:{bind_port}")
    
    while True:
        # Accept incoming connections 
        client_socket, addr = server.accept()
        print(f"[*] Accepted connection from: {addr[0]}:{addr[1]}")
        
        # Spin up a thread to handle the client 
        client_handler = threading.Thread(target=hanle_client, args=(client_socket,))
        client_handler.start()
    
if __name__ == "__main__":
    main()