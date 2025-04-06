import ipaddress
import socket

# determine if an ip address is a public ip
def is_public_ip(ip_address):
    try:
        ip_object = ipaddress.ip_address(ip_address)
    
        if ip_object.is_private:
            return False
        
        # check if it's a reserved IP (multicast, link-local, etc.)
        # https://en.wikipedia.org/wiki/Reserved_IP_addresses
        reserved_ranges = [
            ipaddress.IPv4Network("224.0.0.0/4"),     # multicast addresses
            ipaddress.IPv4Network("169.254.0.0/16"),  # link-local addresses
            ipaddress.IPv4Network("240.0.0.0/4"),     # reserved for future use
            ipaddress.IPv4Network("192.0.2.0/24"),    # documentation/test addresses
            ipaddress.IPv4Network("198.51.100.0/24"), # documentation/test addresses
            ipaddress.IPv4Network("203.0.113.0/24"),  # documentation/test addresses
        ]
        
        # check if the IP falls into any reserved range
        for reserved_range in reserved_ranges:
            if ip_object in reserved_range:
                return False

        return True  # it's a public, non-reserved IP
    except ValueError as e:
        print(f"Error: {e}")
        return False

# get the domain name for a public ip address
def get_domain_name(ip_address):
    try:
        hostname = socket.gethostbyaddr(ip_address)[0]
        return hostname
    except socket.herror:
        print("Domain name not found")