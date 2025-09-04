import socket
import ipaddress

def get_local_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "127.0.0.1"

def validate_ip(ip_address):
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False

def get_timestamp():
    from datetime import datetime
    return datetime.now().isoformat()
