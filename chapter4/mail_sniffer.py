# Import Scapy's sniff function to capture packets from a network interface.
from scapy.all import sniff


# Called once for each captured packet.
def packet_callback(packet):
    # Print a decoded view of every layer in this packet.
    print(packet.show())


# Start the sniffer.
def main():
    # Capture one packet (count=1) and pass it to packet_callback (prn=...).
    sniff(prn=packet_callback, count=1)


# Run main() only when this file is executed directly, not when imported.
if __name__ == "__main__":
    main()
