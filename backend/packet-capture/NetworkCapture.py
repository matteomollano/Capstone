from scapy.all import sniff, Ether, IP, TCP
import json

def packet_callback(packet):
    # packet.show()
    print(packet.summary())
    
def filter_by_ip(packet, ip):
    if packet.haslayer(IP):
            return packet[IP].src == ip or packet[IP].dst == ip
    return False

def filter_by_port(packet, port):
    if packet.haslayer(IP) and packet.haslayer(TCP):
        if packet[TCP].dport == port or packet[TCP].sport == port:
            return True
    return False

def packet_to_dict(packet):
    layers = {}
    while packet:
        layer_name = packet.name
        layer_fields = packet.fields
        layers[layer_name] = {}
        for field, value in layer_fields.items():
            if isinstance(value, bytes):  
                layers[layer_name][field] = value.hex() # convert bytes to hex
            elif isinstance(value, set):  
                layers[layer_name][field] = list(value) # convert sets to lists
            elif isinstance(value, type) or hasattr(value, "__str__"):  
                layers[layer_name][field] = str(value)  # convert special Scapy objects (like FlagValue) to strings
            else:
                layers[layer_name][field] = value
        # layers[layer_name] = packet.fields
        packet = packet.payload
    return layers

def dict_to_json(dict):
    return json.dumps(dict)

def handle_packet(packet):
    print(packet_to_dict(packet))
    print(f'Source MAC Address: {packet[Ether].src}')
    print(f'Dest MAC Address: {packet[Ether].dst}')
    print(f'Source IP Address: {packet[IP].src}')
    print(f'Dest IP Address: {packet[IP].dst}')
    print(f'Protocol: {packet.proto}')
    print("\n---------------------------------\n")

protocol_counts = {}
def get_protocol_counts(packet):
    global protocol_counts

    if packet.proto not in protocol_counts:
        protocol_counts[packet.proto] = 1
    else:
        protocol_counts[packet.proto] += 1
        
    print(protocol_counts)
    print("\n---------------------------------\n")
    
def filter_by_broadcast(packet):
    if packet[IP].src == '255.255.255.255' or packet[IP].dst == '255.255.255.255':
        print(packet_to_dict(packet))
        print("\n---------------------------------\n")

# filter_handler = partial(filter_by_ip, ip='192.168.3.74')
# filter_handler = partial(filter_by_port, port=443)
# sniff(iface="en0", prn=packet_callback, lfilter=filter_handler, store=False)

# packet = sniff(iface="en0", count=1)[0]
# packet_dict = packet_to_dict(packet)
# packet_json = dict_to_json(packet_dict)

# print(packet_dict)
# packet.show()
# print(packet_json)

sniff(prn=filter_by_broadcast, store=False)