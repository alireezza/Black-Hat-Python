#!/usr/bin/env python3
import socket
import argparse
import sys 
def main():
    # 1. THE RECEPTIONIST OF ARGUMENTS
    parser = argparse.ArgumentParser(description="A simple TCP client.")
    
    # We add twor arguments: -t for the target host and -p for the target port.
    parser.add_argument("-t", "--target", type=str, required=True, help="Target host to connect to.")
    parser.add_argument("-p", "--port", type=int, required=True, help="Target port to connect to.")
    
    # We grab the arguments from the terminal 
    args = parser.parse_args()
    
    # Store the in variables for easy access
    target_host = args.target
    target_port = args.port
    
    print(f"[*] Connecting to {target_host}:{target_port}...")
    
    # 2. THE SAFETY NET (Try/Except block)
    client = None
    try:
        # 3. Create a socket object 
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # 4. Connect the client to the target host and port 
        client.connect((target_host, target_port))
        
        # 5. Send some data to the server 
        client.send(b'GET / HTTP/1.1\r\nHost: google.com\r\n\r\n')
        
        # 6. Receive some data from the server 
        response = client.recv(4096) 
        
        # 7. Print the response from the server
        print(response.decode()) 
        
    except Exception as e:
        print(f"[!] An error occurred: {e}")
    
    finally:
        # 8. Close the client socket
        if client is not None:
            client.close()
if __name__ == "__main__":
    main()
    
    
            