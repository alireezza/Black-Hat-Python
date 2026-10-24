import argparse
import getpass
import select
import socket
import sys
import threading

import paramiko


def verbose(message):
    print(message)


def parse_options():
    parser = argparse.ArgumentParser(
        description='Set up a reverse SSH port forward.'
    )
    parser.add_argument(
        'server',
        nargs=2,
        metavar=('HOST', 'PORT'),
        help='SSH server host and port',
    )
    parser.add_argument(
        '-u',
        '--user',
        default=getpass.getuser(),
        help='SSH username',
    )
    parser.add_argument(
        '-p',
        '--port',
        type=int,
        required=True,
        help='Port to forward on the remote SSH server',
    )
    parser.add_argument(
        '-H',
        '--remote-host',
        default='localhost',
        help='Host to connect to on the local network',
    )
    parser.add_argument(
        '-P',
        '--remote-port',
        type=int,
        default=80,
        help='Port to connect to on the remote host',
    )
    parser.add_argument(
        '-k',
        '--keyfile',
        help='Private key file to use for SSH authentication',
    )
    parser.add_argument(
        '--look-for-keys',
        action='store_true',
        help='Look for SSH keys in the standard SSH directories',
    )
    parser.add_argument(
        '--readpass',
        action='store_true',
        help='Prompt for the SSH password',
    )

    options = parser.parse_args()
    server = (options.server[0], int(options.server[1]))
    remote = (options.remote_host, options.remote_port)
    return options, server, remote


def main(): 
    options, server, remote = parse_options() 
    password = None 
    if options.readpass: 
        password = getpass.getpass('Enter SSH password: ')
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
    
    verbose('Connecting to ssh host %s:%d ...' % (server[0], server[1]))
    try: 
        client.connect(server[0], 
                       server[1], 
                       username=options.user, 
                       key_filename=options.keyfile,
                       look_for_keys=options.look_for_keys,
                       password=password
        )
    except Exception as e: 
        print('*** Failed to connect to %s:%d: %r' % (server[0], server[1], e))
        sys.exit(1) 
    
    verbose(
        'Now forwarding remote port %d to %s:%d ...'
        % (options.port, remote[0], remote[1])
    )
    
    try: 
        reverse_forward_tunnel(
            options.port, remote[0], remote[1], client.get_transport()
        )
    except KeyboardInterrupt:
        print('C-c: Port forwarding stopped.')
        sys.exit(0) 
def reverse_forward_tunnel(server_port, remote_host, remote_port, transport):
    transport.request_port_forward('', server_port)
    while True:
        chan = transport.accept(1000)
        if chan is None:
            continue
        thr = threading.Thread(
            target=handler, args=(chan, remote_host, remote_port)
        )
        thr.setDaemon(True)
        thr.start()
def handler(chan, host, port):
    sock = socket.socket()
    try:
        sock.connect((host, port))
    except Exception as e:
        verbose('Forwarding request to %s:%d failed: %r' % (host, port, e))
        return
    print('Connected! Tunnel open %r -> %r -> %r' % (chan.origin_addr, chan.getpeername(), (host, port)))
    while True:
        r, w, x = select.select([sock, chan], [], [])
        if sock in r:
            data = sock.recv(1024)
            if len(data) == 0:
                break
            chan.send(data)
        if chan in r:
            data = chan.recv(1024)
            if len(data) == 0:
                break
            sock.send(data)
    chan.close()
    sock.close()
    print('Tunnel closed from %r' % (chan.origin_addr,))
        