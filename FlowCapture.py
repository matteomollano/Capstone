from scapy.all import sniff, IP
from collections import defaultdict
from datetime import datetime
import time, json

# create a default dictionary for flow data
flows = defaultdict(lambda: {
    'num_packets': 0, 
    'ttl_src': None, 
    'ttl_dst': None, 
    'ttl_states': set(),
    'bytes_src': 0, 
    'bytes_dst': 0,
    'load_src': 0,
    'load_dst': 0,
    'mean_size_src': 0, 
    'mean_size_dst': 0,
    'rate': 0,
    'start_time': None, 
    'end_time': None,
    'packets': list()
})

# get the 5-tuple key
def get_flow_key(packet):
    ip1, ip2 = sorted([packet[IP].src, packet[IP].dst])  # sort ips
    port1, port2 = sorted([packet.sport, packet.dport])  # sort ports
    return (ip1, ip2, port1, port2, packet.proto), (packet[IP].src == ip1)

# convert packet to a dictionary
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

def get_duration(start_time: datetime, end_time: datetime):
    time_difference = end_time - start_time
    td_seconds = time_difference.seconds
    td_microseconds = time_difference.microseconds
    td_ms_in_seconds = td_microseconds / 1000000
    
    print('start time:', start_time)
    print('end time:', end_time)
    print('time dif:', time_difference)
    print('time dif s:', td_seconds)
    print('time dif ms:', td_microseconds)
    
    # return td_seconds + td_ms_in_seconds
    return time_difference.total_seconds()

# process each sniffed packet
def process_packet(packet):
    try:
        if packet.haslayer(IP) and packet[IP].dst != '255.255.255.255':
            flow_key, is_original_src = get_flow_key(packet)
            flow = flows[flow_key]
            
            # track first and last packet time (needed to calculate duration)
            if flow['start_time'] is None:
                flow['start_time'] = datetime.now()
            time.sleep(1)
            flow['end_time'] = datetime.now()
            
            # calculate total duration (needed for rate and load calculations)
            total_duration = get_duration(flow['start_time'], flow['end_time'])
            print('total duration:', total_duration)
            # flow['start_time'] = flow['start_time'].strftime('%Y-%m-%d %H:%M:%S.%f')
            # flow['end_time'] = flow['end_time'].strftime('%Y-%m-%d %H:%M:%S.%f')
            
            # track packets and bytes per direction
            flow['num_packets'] += 1
            if is_original_src:  # if packet is from src -> dst (request packet)
                flow['ttl_src'] = packet[IP].ttl
                flow['bytes_src'] += len(packet)
                flow['load_src'] = (flow['bytes_src'] * 8) / max(0.0001, total_duration) # avoid division by zero
            else:  # if packet is from dst -> src (response packet)
                flow['ttl_dst'] = packet[IP].ttl
                flow['bytes_dst'] += len(packet)
                flow['load_dst'] = (flow['bytes_dst'] * 8) / max(0.0001, total_duration)
                
            # track unique TTL values seen
            flow['ttl_states'].add(packet[IP].ttl)

            # calculate additional statistics
            flow['mean_size_src'] = flow['bytes_src'] / max(1, flow['num_packets'])
            flow['mean_size_dst'] = flow['bytes_dst'] / max(1, flow['num_packets'])
            flow['rate'] = flow['num_packets'] / max(0.0001, total_duration)
            
            # add packet dictionary to flows
            flow['packets'].append(packet_to_json(packet))
            
            # display the flow
            print(f"Key: {flow_key}")
            print(f"Data: {flow}")
            
            print("\n--------------------------------------------------------------------------------------------------\n")
    except Exception as e:
        print("\n\n---------------------------------------------ERROR---------------------------------------------")
        print(f"Error processing packet: {e}")
        print("---------------------------------------------ERROR---------------------------------------------\n\n") 
        
def test(packet):
    if packet.haslayer(IP) and packet[IP].dst == '255.255.255.255':
        print(f"Captured Packet: {packet[IP].src} → {packet[IP].dst}")

# sniff packets
print("Sniffing packets... Press Ctrl+C to stop.")
sniff(filter="ip", prn=process_packet, store=False)