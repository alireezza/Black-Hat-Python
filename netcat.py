import argparse 
import socket
import threading
import subprocess
import shlex 
import sys 
import textwrap

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return 
    try: 
        output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
        return output.decode()
    except subprocess.CalledProcessError as e:
        return e.output.decode()
    except Exception as e:
        return f"Failed to execute command: {str(e)}"

class Netcat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        print(f"[*] Listening on {self.args.target}:{self.args.port}")

        while True:
            client_socket, addr = self.socket.accept()
            print(f"[*] Accepted connection from: {addr[0]}:{addr[1]}")
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

    def handle_client(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        
        elif self.args.upload:
            file_buffer = b""
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                file_buffer += data
            
            with open(self.args.upload, "wb") as f:
                f.write(file_buffer)
            client_socket.send(b"Successfully saved file to %s\n" % self.args.upload.encode())
        
        elif self.args.command:
            while True:
                client_socket.send(b"<BHP:#> ")
                cmd_buffer = b""
                while b"\n" not in cmd_buffer:
                    cmd_buffer += client_socket.recv(1024)
                response = execute(cmd_buffer.decode())
                if response:
                    client_socket.send(response.encode())
        
        client_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Netcat Replacement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Example:
            netcat.py -t 127.0.0.1 -p 8080
        ''')
    )
    parser.add_argument("-t", "--target", help="Target host")
    parser.add_argument("-p", "--port", type=int, help="Target port")
    parser.add_argument("-l", "--listen", action="store_true", help="Listen mode")
    parser.add_argument("-e", "--execute", help="Execute command")
    parser.add_argument("-u", "--upload", help="Upload file")
    parser.add_argument("-c", "--command", action="store_true", help="Command mode")

    args = parser.parse_args()
    if args.listen:
        if not args.target:
            args.target = "0.0.0.0"

    nc = Netcat(args)
    nc.run()