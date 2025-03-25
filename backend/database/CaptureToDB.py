from scapy.all import sniff, IP, TCP, UDP
import json
from utils import check_flow_exists, insert_new_flow, update_flow

# get the 5-tuple key
def get_flow_key(packet):
    ip1, ip2 = sorted([packet[IP].src, packet[IP].dst])  # sort ips
    
    # if the packet doesn't have ports, we set the ports to None
    if packet.haslayer(TCP) or packet.haslayer(UDP):
        port1, port2 = sorted([packet.sport, packet.dport])  # sort ports
    else:
        port1, port2 = None, None  # no ports for ICMP, IGMP, etc.
        
    return (ip1, ip2, port1, port2, packet.proto), (packet[IP].src == ip1)


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


# process each sniffed packet
def process_packet(packet):
    try:
        # disregard broadcasts
        if packet.haslayer(IP) and packet[IP].dst == '255.255.255.255':
            return
        
        # get flow key and is_original_src boolean
        flow_key, is_original_src = get_flow_key(packet)
        
        # packet data as json for Packets table
        packet_data = packet_to_json(packet)
        
        # check if the flow exists in the database
        if not check_flow_exists(flow_key):
            # if it doesn't exist, then create a new flow record
            insert_new_flow(flow_key, is_original_src, packet, packet_data)
        else:
            # if the flow does already exist, then update it
            update_flow(flow_key, is_original_src, packet, packet_data)
            
        print("\n--------------------------------------------------------------------------------------------------\n")
    except Exception as e:
        print("\n\n---------------------------------------------ERROR---------------------------------------------")
        print(f"Error processing packet: {e}")
        print("---------------------------------------------ERROR---------------------------------------------\n\n")

# sniff packets
print("Sniffing packets... Press Ctrl+C to stop.")
sniff(filter="ip", prn=process_packet, store=False)