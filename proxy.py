#!/usr/bin/env python3

import sys
import socket
import threading

HEX_FILTER = ''.join(
    (len(repr(chr(i))) == 3) and chr(i) or '.'
    for i in range(256)
)


def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):
        src = src.decode(errors='replace')

    results = []

    for i in range(0, len(src), length):
        word = str(src[i:i + length])
        printable = word.translate(HEX_FILTER)
        hexa = ' '.join(f"{ord(c):02X}" for c in word)
        hexwidth = length * 3

        results.append(
            f"{i:04x}   {hexa:<{hexwidth}}   {printable}"
        )

    if show:
        for line in results:
            print(line)
    else:
        return results


def receive_from(connection):
    buffer = b""
    connection.settimeout(2)

    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except socket.timeout:
        pass
    except OSError as e:
        print(f"[!] Receive error: {e}")

    return buffer


def request_handler(buffer):
    # Perform packet modifications here.
    return buffer


def response_handler(buffer):
    # Perform packet modifications here.
    return buffer


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        remote_socket.connect((remote_host, remote_port))

        remote_buffer = b""

        if receive_first:
            remote_buffer = receive_from(remote_socket)

            if remote_buffer:
                print(f"[<==] Received {len(remote_buffer)} bytes from remote.")
                hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)

            if remote_buffer:
                client_socket.sendall(remote_buffer)

        while True:
            local_buffer = receive_from(client_socket)

            if local_buffer:
                print(f"[==>] Received {len(local_buffer)} bytes from localhost.")
                hexdump(local_buffer)

                local_buffer = request_handler(local_buffer)
                remote_socket.sendall(local_buffer)
                print("[==>] Sent to remote.")

            remote_buffer = receive_from(remote_socket)

            if remote_buffer:
                print(f"[<==] Received {len(remote_buffer)} bytes from remote.")
                hexdump(remote_buffer)

                remote_buffer = response_handler(remote_buffer)
                client_socket.sendall(remote_buffer)
                print("[<==] Sent to localhost.")

            if not local_buffer or not remote_buffer:
                print("[*] No more data. Closing connections.")
                break

    except OSError as e:
        print(f"[!] Proxy connection error: {e}")

    finally:
        client_socket.close()
        remote_socket.close()


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((local_host, local_port))
        server.listen(5)

    except OSError as e:
        print(f"[!] Failed to listen on {local_host}:{local_port}: {e}")
        server.close()
        sys.exit(1)

    print(f"[*] Listening on {local_host}:{local_port}")

    try:
        while True:
            client_socket, addr = server.accept()
            print(f"[==>] Incoming connection from {addr[0]}:{addr[1]}")

            proxy_thread = threading.Thread(
                target=proxy_handler,
                args=(
                    client_socket,
                    remote_host,
                    remote_port,
                    receive_first
                ),
                daemon=True
            )
            proxy_thread.start()

    except KeyboardInterrupt:
        print("\n[*] Shutting down proxy.")

    finally:
        server.close()


def main():
    if len(sys.argv) != 6:
        print(
            "Usage: python3 proxy.py "
            "[localhost] [localport] "
            "[remotehost] [remoteport] [receive_first]"
        )
        print(
            "Example: python3 proxy.py "
            "127.0.0.1 8080 127.0.0.1 8081 True"
        )
        sys.exit(1)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5].lower() == "true"

    server_loop(
        local_host,
        local_port,
        remote_host,
        remote_port,
        receive_first
    )


if __name__ == "__main__":
    main()

