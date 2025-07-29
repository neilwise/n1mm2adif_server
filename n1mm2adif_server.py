import socket
import xml.etree.ElementTree as ET
import os

# === Configuration ===
UDP_IP = "0.0.0.0"
UDP_PORT = 12060
LOG_FILE = r"C:\Users\neil\Documents\N1MM Logger+\ExportFiles\auto_adi\qso_log.adi"

# === Band Mapping ===
def determine_band(freq_mhz: float) -> str:
    if 1.8 <= freq_mhz < 2.0:
        return "160m"
    elif 3.5 <= freq_mhz < 4.0:
        return "80m"
    elif 7.0 <= freq_mhz < 7.3:
        return "40m"
    elif 10.1 <= freq_mhz < 10.15:
        return "30m"
    elif 14.0 <= freq_mhz < 14.35:
        return "20m"
    elif 18.068 <= freq_mhz < 18.168:
        return "17m"
    elif 21.0 <= freq_mhz < 21.45:
        return "15m"
    elif 24.89 <= freq_mhz < 24.99:
        return "12m"
    elif 28.0 <= freq_mhz < 29.7:
        return "10m"
    elif 50.0 <= freq_mhz < 54.0:
        return "6m"
    elif 70.0 <= freq_mhz < 71.0:
        return "4m"
    elif 144.0 <= freq_mhz < 148.0:
        return "2m"
    elif 430.0 <= freq_mhz < 440.0:
        return "70cm"
    elif 1296.0 <= freq_mhz < 1300.0:
        return "23cm"
    elif 2300.0 <= freq_mhz < 2410.0:
        return "13cm"
    elif 3400.0 <= freq_mhz < 3500.0:
        return "9cm"
    elif 5760.0 <= freq_mhz < 5770.0:
        return "6cm"
    elif 10300.0 <= freq_mhz < 10500.0:
        return "3cm"
    return "unknown"

# === XML Parsing ===
def parse_contactinfo(xml_data: str) -> dict:
    root = ET.fromstring(xml_data)

    def get(tag, default=""):
        elem = root.find(tag)
        return elem.text.strip() if elem is not None and elem.text else default

    tx_freq_raw = int(get("txfreq", "0"))
    freq_mhz = tx_freq_raw * 10 / 1_000_000.0  # 10 Hz units → MHz
    freq_str = f"{freq_mhz:.6f}"

    band = determine_band(freq_mhz)  # MHz for band lookup

    rx_freq_raw = int(get("rxfreq", "0"))
    rx_freq_mhz = rx_freq_raw * 10 / 1_000_000.0  # 10 Hz units → MHz
    rx_freq_str = f"{rx_freq_mhz:.6f}"

    timestamp = get("timestamp", "0000-00-00 00:00:00")
    oldtimestamp = get("oldtimestamp", timestamp)

    return {
        "call": get("call"),
        "gridsquare": get("gridsquare"),
        "mode": get("mode"),
        "rst_sent": get("snt"),
        "rst_rcvd": get("rcv"),
        "srx": get("rcvnr"),
        "stx": get("sntnr"),
        "qso_date": timestamp.split()[0].replace("-", ""),
        "time_on": timestamp.split()[1].replace(":", ""),
        "qso_date_off": oldtimestamp.split()[0].replace("-", ""),
        "time_off": oldtimestamp.split()[1].replace(":", ""),
        "band": band,
        "freq": freq_str,
        "freq_rx": rx_freq_str,
        "station_callsign": get("mycall"),
        "my_gridsquare": get("my_gridsquare", "IO91HP"),
        "tx_pwr": get("power", "100W"),
        "comment": f"{get('contestname')}  Sent: {get('snt')} {get('sntnr')}  Rcvd: {get('rcv')} {get('rcvnr')}",
        "operator": get("mycall"),
    }

# === Format Line for Log File ===
# note that VQLOG doesn't action the following in WSJT adi file monitoring mode
# srx
# stx
# freq_rx
#
# my_gridsquare doesn't seem to be available from N1MM 
# power from N1MM is pwr RXd from other station rather than tx_pwr 
 
def format_log_line(fields: dict) -> str:
    return (
        f"<call:{len(fields['call'])}>{fields['call']} "
        f"<gridsquare:{len(fields['gridsquare'])}>{fields['gridsquare']} "
        f"<mode:{len(fields['mode'])}>{fields['mode']} "
        f"<rst_sent:{len(fields['rst_sent'])}>{fields['rst_sent']} "
        f"<rst_rcvd:{len(fields['rst_rcvd'])}>{fields['rst_rcvd']} "
        f"<srx:{len(fields['srx'])}>{fields['srx']} "
        f"<stx:{len(fields['stx'])}>{fields['stx']} "
        f"<qso_date:8>{fields['qso_date']} "
        f"<time_on:6>{fields['time_on']} "
        f"<qso_date_off:8>{fields['qso_date_off']} "
        f"<time_off:6>{fields['time_off']} "
        f"<band:{len(fields['band'])}>{fields['band']} "
        f"<freq:{len(fields['freq'])}>{fields['freq']} "
        f"<freq_rx:{len(fields['freq_rx'])}>{fields['freq_rx']} "
        f"<station_callsign:{len(fields['station_callsign'])}>{fields['station_callsign']} "
        f"<my_gridsquare:{len(fields['my_gridsquare'])}>{fields['my_gridsquare']} "
        f"<tx_pwr:{len(fields['tx_pwr'])}>{fields['tx_pwr']} "
        f"<comment:{len(fields['comment'])}>{fields['comment']} "
        f"<operator:{len(fields['operator'])}>{fields['operator']} <eor>"
    )

# === UDP Server ===
def start_udp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Listening for UDP packets on port {UDP_PORT}...\n")

    while True:
        data, addr = sock.recvfrom(4096)
        print(f"Packet received from {addr}")

        try:
            xml_text = data.decode('utf-8')
            root = ET.fromstring(xml_text)
            if root.tag != 'contactinfo':
                print("Invalid root tag; skipping.")
                continue

            fields = parse_contactinfo(xml_text)
            log_line = format_log_line(fields)

            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")

            print("Logged QSO:")
            print(log_line + "\n")

        except Exception as e:
            print(f"Failed to parse or log packet: {e}\n")

if __name__ == "__main__":
    start_udp_server()
