from scapy.all import ETHER_TYPES, IP_PROTOS
from database.common_ports import COMMON_PORTS

# function to convert a protocol name to its corresponding protocol number
def get_protocol_number(proto_name):
    proto_name = str(proto_name).lower()
    
    # check COMMON_PORTS first (reverse the mapping)
    common_ports_map = {str(v).lower(): k for k, v in COMMON_PORTS.items()}
    if proto_name in common_ports_map:
        return common_ports_map[proto_name]
    
    # check IP_PROTOS second
    ip_proto_map = {str(IP_PROTOS[i]).lower(): i for i in IP_PROTOS}
    if proto_name in ip_proto_map:
        return ip_proto_map[proto_name]
    
    # check ETHER_TYPES last
    ether_map = {str(ETHER_TYPES[i]).lower(): i for i in ETHER_TYPES}
    if proto_name in ether_map:
        return ether_map[proto_name]
    
    return None