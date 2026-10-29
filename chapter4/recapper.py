
from scapy.all import TCP, rdpcap
import collections
import os
import re
import sys
import zlib

OUTDIR = '/root/Desktop/pictures'
PCAPS = '/root/Downloads'

Response = collections.namedtuple('Response', ['header', 'payload'])


def get_header(payload):
    try:
        end = payload.index(b'\r\n\r\n')
        header_raw = payload[:end + 2]
    except ValueError:
        sys.stdout.write('-')
        sys.stdout.flush()
        return None

    header_text = header_raw.decode('iso-8859-1')
    header = dict(
        re.findall(r'(?P<name>.*?): (?P<value>.*?)\r\n', header_text)
    )

    if 'Content-Type' not in header:
        return None

    return header


def extract_content(response, content_name='image'):
    content, content_type = None, None
    header = response.header

    if content_name in header.get('Content-Type', ''):
        content_type = header['Content-Type'].split(';')[0].split('/')[-1]
        content = response.payload[
            response.payload.index(b'\r\n\r\n') + 4:
        ]

        encoding = header.get('Content-Encoding', '').lower()

        try:
            if encoding == 'gzip':
                content = zlib.decompress(
                    content, zlib.MAX_WBITS | 32
                )
            elif encoding == 'deflate':
                content = zlib.decompress(content)
        except zlib.error:
            return None, None

    return content, content_type


class Recapper:
    def __init__(self, fname):
        pcap = rdpcap(fname)
        self.session = pcap.sessions()
        self.responses = []

    def get_responses(self):
        for session in self.session:
            payload = b''

            for packet in self.session[session]:
                if TCP not in packet:
                    continue

                if packet[TCP].dport == 80 or packet[TCP].sport == 80:
                    payload += bytes(packet[TCP].payload)

            if payload:
                header = get_header(payload)

                if header is None:
                    continue

                self.responses.append(
                    Response(header=header, payload=payload)
                )

    def write(self, content_name):
        os.makedirs(OUTDIR, exist_ok=True)

        for i, response in enumerate(self.responses):
            content, content_type = extract_content(
                response, content_name
            )

            if content and content_type:
                fname = os.path.join(
                    OUTDIR, f'ex{i}.{content_type}'
                )
                print(f'Writing {fname}')

                with open(fname, 'wb') as f:
                    f.write(content)


if __name__ == '__main__':
    profile = os.path.join(PCAPS, 'pcap.pcap')
    recapper = Recapper(profile)
    recapper.get_responses()
    recapper.write('image')
