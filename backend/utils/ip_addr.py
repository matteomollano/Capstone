import ipaddress
import socket

# determine if an ip address is a public ip
def is_public_ip(ip_address):
    try:
        ip_object = ipaddress.ip_address(ip_address)
        return not ip_object.is_private
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