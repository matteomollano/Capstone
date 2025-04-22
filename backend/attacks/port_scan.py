from scapy.all import IP, TCP, sr

# source: https://denizhalil.com/2025/01/14/port-scanning-with-scapy/
def port_scan(target_ip, start_port, end_port):
    open = []
    closed = []
    filtered = []
    for port in range(start_port, end_port + 1):
        response = sr(IP(dst=target_ip) / TCP(dport=port, flags="S"), timeout=1, verbose=0)[0]
        if response:
            for sent, received in response:
                if received.haslayer(TCP) and received[TCP].flags == 18:    # SYN-ACK (SA)
                    # print(f"Port {port} is open")
                    open.append(port)
                elif received.haslayer(TCP) and received[TCP].flags == 20:  # RST (RA)
                    # print(f"Port {port} is closed")
                    closed.append(port)
        else:
            # print(f"Port {port} is filtered or no response")
            filtered.append(port)
    return open, closed, filtered
        
target_ip = "192.168.10.1"
start_port = 1
end_port = 1024

open, closed, filtered = port_scan(target_ip, start_port, end_port)
print(f"Open ports: {', '.join(map(lambda x: str(x), open))}")
print(f"Closed ports: {', '.join(map(lambda x: str(x), closed))}")
print(f"Filtered ports: {', '.join(map(lambda x: str(x), filtered))}")