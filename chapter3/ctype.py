from ctypes import * 
import socket 
import struct 

class IP(Structure): 
    _field_ = [ 
               ("version", c_ubyte, 4), # 4 bytes for the version
               ("ihl", c_ubyte, 4), # 4 bytes for the IHL
               ("tos", c_ubyte, 8), # 8 bytes for the TOS
               ("len", c_ushort, 16), # 16 bytes for the length
               ("id", c_ushort, 16), # 16 bytes for the ID
               ("offset", c_ushort, 16), # 16 bytes for the offset
               ("ttl", c_ubyte, 8), # 8 bytes for the TTL
               ("protocol", c_ubyte, 8), # 8 bytes for the protocol
               ("sum", c_ushort, 16), # 16 bytes for the checksum
               ("src", c_ulong, 32), # 32 bytes for the source address
               ("dst", c_ulong, 32), # 32 bytes for the destination address
            ]
            def __new__(self, socket_buffer=None):
                return cls.from_buffer_copy(socket_buffer)
            def __init__(self, socket_buffer=None):
                # human readable IP addresses 
                self.src_address = socket.inet_ntoa(struct.pack("<L", self.src))
                self.dst_address = socket.inet_ntoa(struct.pack("<L", self.dst))