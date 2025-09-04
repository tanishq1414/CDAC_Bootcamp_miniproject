import random
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DynamicFirewall:
    def __init__(self, socketio=None):
        self.ports = [80, 443, 8080, 8443, 22, 3389]  # Common service ports
        self.current_open_ports = []
        self.rotation_interval = 30  # seconds
        self.attack_log = []
        self.suspicious_ips = {}
        self.socketio = socketio
        
    def rotate_ports(self):
        """Simulate firewall port rotation"""
        # Close 1-2 ports and open 1-2 new ones
        ports_to_close = min(2, len(self.current_open_ports))
        ports_to_open = random.randint(1, 2)
        
        if self.current_open_ports:
            for _ in range(ports_to_close):
                port = random.choice(self.current_open_ports)
                self.current_open_ports.remove(port)
                logger.info(f"Firewall closed port {port}")
        
        for _ in range(ports_to_open):
            available_ports = [p for p in self.ports if p not in self.current_open_ports]
            if available_ports:
                new_port = random.choice(available_ports)
                self.current_open_ports.append(new_port)
                logger.info(f"Firewall opened port {new_port}")
        
        # Ensure we always have at least one port open
        if not self.current_open_ports:
            self.current_open_ports.append(random.choice(self.ports))
        
        # Notify dashboard of the change
        if self.socketio:
            self.socketio.emit('firewall_update', self.get_status())
    
    def start_rotation(self):
        """Continuously rotate firewall rules"""
        # Start with some open ports
        self.current_open_ports = random.sample(self.ports, 3)
        logger.info(f"Initial open ports: {self.current_open_ports}")
        
        # Initial notification
        if self.socketio:
            self.socketio.emit('firewall_update', self.get_status())
        
        while True:
            time.sleep(self.rotation_interval)
            self.rotate_ports()
    
    def check_access(self, src_ip, dst_port):
        """Check if access is allowed and log potential attacks"""
        is_allowed = dst_port in self.current_open_ports
        
        if not is_allowed:
            self.log_attack(src_ip, dst_port, "Port scanning")
            # Add to suspicious IPs
            if src_ip in self.suspicious_ips:
                self.suspicious_ips[src_ip] += 1
            else:
                self.suspicious_ips[src_ip] = 1
                
            # If highly suspicious, redirect to honeypot on next attempt
            if self.suspicious_ips.get(src_ip, 0) > 2:
                return "redirect_to_honeypot"
        
        return is_allowed
    
    def log_attack(self, ip, port, attack_type):
        """Log attack attempts"""
        attack_entry = {
            "timestamp": datetime.now().isoformat(),
            "ip": ip,
            "port": port,
            "type": attack_type,
            "action": "blocked"
        }
        self.attack_log.append(attack_entry)
        logger.warning(f"Attack detected: {attack_type} from {ip} on port {port}")
        
        # Notify dashboard of the new attack
        if self.socketio:
            self.socketio.emit('firewall_attack', attack_entry)
            self.socketio.emit('firewall_update', self.get_status())

    def get_status(self):
        """Return current firewall status for dashboard"""
        return {
            "open_ports": self.current_open_ports,
            "rotation_interval": self.rotation_interval,
            "attack_count": len(self.attack_log),
            "suspicious_ips": self.suspicious_ips,
            "recent_attacks": self.attack_log[-10:] if self.attack_log else []
        }