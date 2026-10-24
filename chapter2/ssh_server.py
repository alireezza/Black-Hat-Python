import os 
import paramiko 
import socket 
import sys 
import threading 

CWD = os.path.dirname(os.path.realpath(__file__))
HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, 'test_rsa.key'))

class Server(paramiko.ServerInterface):
    def _init__(self):
        self.event = threading.Event()
        
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    def check_auth_password(self, username, password):
        if (username == 'testuser') and (password == 'testpass'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

if __name__ == '__main__':
    server = 'localhost'
    ssh_port = 2200
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server, ssh_port))
    except Exception as e:
        print(f'Bind failed: {e}')
        sys.exit(1)
    sock.listen(100)
    print(f'Listening for connection on {server}:{ssh_port} ...')
    
    while True:
        client, addr = sock.accept()
        print(f'Got a connection from {addr}')
        transport = paramiko.Transport(client)
        transport.add_server_key(HOSTKEY)
        server = Server()
        try:
            transport.start_server(server=server)
        except paramiko.SSHException:
            print('SSH negotiation failed.')
            continue
        
        chan = transport.accept(20)
        if chan is None:
            print('No channel.')
            continue
        print('Authenticated!')
        
        chan.send('Welcome to the SSH server!\n')
        while True:
            try:
                command = chan.recv(1024).decode('utf-8')
                if not command:
                    break
                print(f'Received command: {command}')
                response = f'You said: {command}\n'
                chan.send(response)
            except Exception as e:
                print(f'Error: {e}')
                break
        chan.close()
        