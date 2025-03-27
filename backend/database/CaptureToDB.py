from scapy.all import sniff, Ether, ARP, IP, TCP, UDP, ETHER_TYPES, IP_PROTOS, IPv6
import json, traceback
from utils import check_flow_exists, insert_new_flow, update_flow
from common_ports import COMMON_PORTS

# get the 5-tuple key
def get_flow_key(packet_layer):
    src_ip, dst_ip, src_port, dst_port, protocol = packet_layer["src_ip_address"], packet_layer["dst_ip_address"], packet_layer["src_port"], packet_layer["dst_port"], packet_layer["protocol"]
    
    ip1, ip2 = sorted([src_ip, dst_ip])  # sort ips
    
    # if the two ports are not None, then sort them
    if src_port is not None and dst_port is not None:
        port1, port2 = sorted([src_port, dst_port])  # sort ports
    # else, set them to None
    else:
        port1, port2 = None, None
    
    return (ip1, ip2, port1, port2, protocol), (src_ip == ip1)


# convert packet to a json object
def packet_to_json(packet):
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
        packet = packet.payload
    return json.dumps(layers)


# get the frame and packet layer from a sniffed packet
def get_layers(packet):
    # initialize all variables as None
    src_ip_address = None
    dst_ip_address = None
    src_port = None
    dst_port = None
    ttl = None
    
    # layer 2 data
    src_mac_address = packet[Ether].src
    dst_mac_address = packet[Ether].dst
    ether_type = packet[Ether].type
    ether_protocol = ETHER_TYPES[ether_type]
    
    protocol = ETHER_TYPES[ether_type]
    packet_length = len(packet)
    
    if packet.haslayer(ARP):
        src_ip_address = packet[ARP].psrc
        dst_ip_address = packet[ARP].pdst
        
    if packet.haslayer(IP) or packet.haslayer(IPv6):
        if packet.haslayer(IP):
            src_ip_address = packet[IP].src
            dst_ip_address = packet[IP].dst
            protocol_num = packet[IP].proto
            ttl = packet[IP].ttl
        else:
            src_ip_address = packet[IPv6].src
            dst_ip_address = packet[IPv6].dst
            protocol_num = packet[IPv6].nh
            ttl = packet[IPv6].hlim
        
        protocol = IP_PROTOS[protocol_num]
        
        if packet.haslayer(TCP):
            src_port = packet[TCP].sport
            dst_port = packet[TCP].dport
            
            if src_port in COMMON_PORTS.keys():
                protocol = COMMON_PORTS[src_port]

            elif dst_port in COMMON_PORTS.keys():
                protocol = COMMON_PORTS[dst_port]
                
        elif packet.haslayer(UDP):
            src_port = packet[UDP].sport
            dst_port = packet[UDP].dport
            
            if src_port in COMMON_PORTS.keys():
                protocol = COMMON_PORTS[src_port]
            
            elif dst_port in COMMON_PORTS.keys():
                protocol = COMMON_PORTS[dst_port]
            
    frame_layer = {
        "src_mac_address": src_mac_address,
        "dst_mac_address": dst_mac_address,
        "ether_type": ether_type,
        "protocol": ether_protocol
    }
    
    packet_layer = {
        "src_ip_address": src_ip_address,
        "dst_ip_address": dst_ip_address,
        "src_port": src_port,
        "dst_port": dst_port,
        "protocol": protocol,
        "ttl": ttl,
        "packet_length": packet_length
    }
    
    return frame_layer, packet_layer


# process each sniffed packet
def process_packet(packet):
    try:
        # get the frame and packet layer of the sniffed packet
        frame_layer, packet_layer = get_layers(packet)
        
        # get flow key and is_original_src boolean
        flow_key, is_original_src = get_flow_key(packet_layer)
        
        # skip over MySQL packets
        port1, port2 = flow_key[2], flow_key[3]
        if port1 == 3306 or port2 == 3306:
            return
        
        # packet data as json for Packets table
        packet_json = packet_to_json(packet)
        
        # check if the flow exists in the database
        if not check_flow_exists(flow_key):
            # if it doesn't exist, then create a new flow record
            insert_new_flow(flow_key, is_original_src, packet_layer, packet_json, frame_layer, debug=False)
        else:
            # if the flow does already exist, then update it
            update_flow(flow_key, is_original_src, packet_layer, packet_json, frame_layer, debug=False)
            
    except Exception as e:
        print("\n\n---------------------------------------------ERROR---------------------------------------------")
        print(traceback.format_exc())
        print("---------------------------------------------ERROR---------------------------------------------\n\n")

# sniff packets
print("Sniffing packets... Press Ctrl+C to stop.")
sniff(prn=process_packet, store=False)