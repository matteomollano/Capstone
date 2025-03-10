from scapy.all import sniff, IP, TCP
from functools import partial
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

# filter_handler = partial(filter_by_ip, ip='192.168.3.74')
# filter_handler = partial(filter_by_port, port=443)
# sniff(iface="en0", prn=packet_callback, lfilter=filter_handler, store=False)

packet = sniff(iface="en0", count=1)[0]
packet_dict = packet_to_dict(packet)
packet_json = dict_to_json(packet_dict)

# print(packet_dict)
# packet.show()
print(packet_json)