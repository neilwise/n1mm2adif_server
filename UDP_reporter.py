import socket
import xml.etree.ElementTree as ET

# Configuration
UDP_IP = "0.0.0.0"
UDP_PORT = 12060  # Change this to match your actual port

def is_valid_contactinfo_packet(data: bytes) -> bool:
    try:
        xml_text = data.decode('utf-8')
        root = ET.fromstring(xml_text)
        return root.tag == 'contactinfo'
    except Exception:
        return False

def print_packet_contents(data: bytes):
    xml_text = data.decode('utf-8')
    print(xml_text)
    print("===========================================\n")

def start_udp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Listening for UDP packets on port {UDP_PORT}...\n")

    while True:
        data, addr = sock.recvfrom(4096)
        print(f"Packet received from {addr}")
        if is_valid_contactinfo_packet(data):
            print("=== Received Valid <contactinfo> Packet ===")
            print_packet_contents(data)
        else:
            print_packet_contents(data)
            # print("Not a valid <contactinfo> XML packet.\n")

if __name__ == "__main__":
    start_udp_server()
