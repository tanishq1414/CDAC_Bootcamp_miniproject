import random
import time
import logging
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)

class DynamicFirewall:
    def __init__(self, socketio=None):
        self.ports = [80, 443, 8080, 8443, 22, 3389, 21, 25, 53, 110, 143, 993, 995, 3306, 27017]  # Extended port list
        self.current_open_ports = []
        self.rotation_interval = 30  # seconds
        self.attack_log = []
        self.suspicious_ips = {}
        self.socketio = socketio
        self.rotation_count = 0
        self.port_history = []
        self.ip_shift_history = []
        self.monitoring_data = {
            "threat_level": 0,
            "attack_patterns": [],
            "real_time_stats": {
                "requests_per_second": 0,
                "blocked_requests": 0,
                "allowed_requests": 0
            }
        }
        self.monitoring_thread = None
        self.is_monitoring = False
        
    def rotate_ports(self):
        """Simulate firewall port rotation with enhanced logging"""
        self.rotation_count += 1
        
        # Store current state before rotation
        previous_ports = self.current_open_ports.copy()
        
        # Close 1-2 ports
        ports_to_close = min(2, len(self.current_open_ports))
        closed_ports = []
        for _ in range(ports_to_close):
            if self.current_open_ports:
                port = random.choice(self.current_open_ports)
                self.current_open_ports.remove(port)
                closed_ports.append(port)
                logger.info(f"Firewall closed port {port}")
        
        # Open 1-2 new ports
        ports_to_open = random.randint(1, 2)
        opened_ports = []
        for _ in range(ports_to_open):
            available_ports = [p for p in self.ports if p not in self.current_open_ports]
            if available_ports:
                new_port = random.choice(available_ports)
                self.current_open_ports.append(new_port)
                opened_ports.append(new_port)
                logger.info(f"Firewall opened port {new_port}")
        
        # Ensure we always have at least 2 ports open
        while len(self.current_open_ports) < 2:
            available_ports = [p for p in self.ports if p not in self.current_open_ports]
            if available_ports:
                new_port = random.choice(available_ports)
                self.current_open_ports.append(new_port)
                opened_ports.append(new_port)
                logger.info(f"Firewall opened additional port {new_port}")
            else:
                break
        
        # Record port history for visualization
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "open_ports": self.current_open_ports.copy(),
            "closed_ports": closed_ports,
            "opened_ports": opened_ports,
            "rotation_count": self.rotation_count
        }
        self.port_history.append(history_entry)
        
        # Keep only recent history
        if len(self.port_history) > 20:
            self.port_history = self.port_history[-20:]
        
        # Record IP shift data
        ip_shift_entry = {
            "timestamp": datetime.now().isoformat(),
            "suspicious_ip_count": len(self.suspicious_ips),
            "new_ips_last_hour": self._get_new_ips_count(),
            "total_attack_count": len(self.attack_log)
        }
        self.ip_shift_history.append(ip_shift_entry)
        
        if len(self.ip_shift_history) > 15:
            self.ip_shift_history = self.ip_shift_history[-15:]
        
        # Update threat level based on activity
        self._update_threat_level()
        
        # Notify dashboard of the change
        if self.socketio:
            self.socketio.emit('firewall_update', self.get_status())
            self.socketio.emit('port_rotation', history_entry)
            self.socketio.emit('ip_shift_update', ip_shift_entry)
    
    def _get_new_ips_count(self):
        """Count IPs that appeared in the last hour"""
        one_hour_ago = datetime.now() - timedelta(hours=1)
        new_ips = 0
        
        for ip, first_seen in self.suspicious_ips.items():
            if isinstance(first_seen, dict) and 'first_seen' in first_seen:
                first_seen_time = datetime.fromisoformat(first_seen['first_seen'])
                if first_seen_time > one_hour_ago:
                    new_ips += 1
        
        return new_ips
    
    def _update_threat_level(self):
        """Calculate threat level based on recent activity"""
        base_threat = min(100, len(self.attack_log) * 2 + len(self.suspicious_ips) * 3)
        
        # Adjust based on recent activity (last 10 minutes)
        recent_attacks = [a for a in self.attack_log 
                         if datetime.fromisoformat(a['timestamp']) > datetime.now() - timedelta(minutes=10)]
        
        activity_bonus = min(30, len(recent_attacks) * 5)
        self.monitoring_data["threat_level"] = min(100, base_threat + activity_bonus)
        
        # Detect patterns
        self._detect_attack_patterns()
    
    def _detect_attack_patterns(self):
        """Simulate ML pattern detection"""
        patterns = []
        
        # Check for port scanning patterns
        port_scan_ips = {}
        for attack in self.attack_log:
            if attack['type'] == 'Port scanning':
                ip = attack['ip']
                if ip in port_scan_ips:
                    port_scan_ips[ip] += 1
                else:
                    port_scan_ips[ip] = 1
        
        for ip, count in port_scan_ips.items():
            if count > 5:
                patterns.append(f"Port scanning pattern detected from {ip} ({count} attempts)")
        
        # Check for brute force patterns
        recent_attacks = [a for a in self.attack_log 
                         if datetime.fromisoformat(a['timestamp']) > datetime.now() - timedelta(minutes=5)]
        
        if len(recent_attacks) > 10:
            patterns.append("High frequency attack pattern detected")
        
        self.monitoring_data["attack_patterns"] = patterns[-5:]  # Keep only recent patterns
    
    def start_rotation(self):
        """Continuously rotate firewall rules"""
        # Start with some open ports
        self.current_open_ports = random.sample(self.ports, 3)
        logger.info(f"Initial open ports: {self.current_open_ports}")
        
        # Start monitoring thread
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        # Initial notification
        if self.socketio:
            self.socketio.emit('firewall_update', self.get_status())
        
        while True:
            time.sleep(self.rotation_interval)
            self.rotate_ports()
    
    def _monitoring_loop(self):
        """Continuous monitoring of firewall activity"""
        while self.is_monitoring:
            # Update real-time statistics
            self.monitoring_data["real_time_stats"] = {
                "requests_per_second": random.randint(5, 50),
                "blocked_requests": len(self.attack_log),
                "allowed_requests": random.randint(100, 500)
            }
            
            # Send monitoring update
            if self.socketio:
                self.socketio.emit('monitoring_update', {
                    "threat_level": self.monitoring_data["threat_level"],
                    "attack_patterns": self.monitoring_data["attack_patterns"],
                    "real_time_stats": self.monitoring_data["real_time_stats"],
                    "timestamp": datetime.now().isoformat()
                })
            
            time.sleep(2)  # Update every 2 seconds
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1)
    
    def check_access(self, src_ip, dst_port):
        """Check if access is allowed and log potential attacks"""
        is_allowed = dst_port in self.current_open_ports
        
        if not is_allowed:
            attack_type = self._classify_attack(dst_port)
            self.log_attack(src_ip, dst_port, attack_type)
            
            # Add to suspicious IPs with timestamp
            if src_ip in self.suspicious_ips:
                if isinstance(self.suspicious_ips[src_ip], dict):
                    self.suspicious_ips[src_ip]['count'] += 1
                    self.suspicious_ips[src_ip]['last_seen'] = datetime.now().isoformat()
                else:
                    # Convert old format to new format
                    self.suspicious_ips[src_ip] = {
                        'count': self.suspicious_ips[src_ip] + 1,
                        'first_seen': datetime.now().isoformat(),
                        'last_seen': datetime.now().isoformat()
                    }
            else:
                self.suspicious_ips[src_ip] = {
                    'count': 1,
                    'first_seen': datetime.now().isoformat(),
                    'last_seen': datetime.now().isoformat()
                }
                
            # If highly suspicious, redirect to honeypot on next attempt
            ip_data = self.suspicious_ips[src_ip]
            if isinstance(ip_data, dict) and ip_data['count'] > 2:
                return "redirect_to_honeypot"
        
        return is_allowed
    
    def _classify_attack(self, port):
        """Classify attack type based on port and pattern"""
        # Common attack patterns by port
        port_attack_types = {
            22: "SSH Brute Force",
            23: "Telnet Attack",
            25: "SMTP Exploit",
            53: "DNS Amplification",
            80: "HTTP Attack",
            443: "HTTPS Attack",
            3389: "RDP Brute Force",
            3306: "SQL Injection",
            27017: "MongoDB Exploit"
        }
        
        return port_attack_types.get(port, "Port scanning")
    
    def log_attack(self, ip, port, attack_type):
        """Log attack attempts with enhanced details"""
        attack_entry = {
            "timestamp": datetime.now().isoformat(),
            "ip": ip,
            "port": port,
            "type": attack_type,
            "action": "blocked",
            "severity": self._assess_severity(attack_type),
            "threat_level": self.monitoring_data["threat_level"]
        }
        self.attack_log.append(attack_entry)
        logger.warning(f"Attack detected: {attack_type} from {ip} on port {port}")
        
        # Notify dashboard of the new attack
        if self.socketio:
            self.socketio.emit('firewall_attack', attack_entry)
            self.socketio.emit('firewall_update', self.get_status())
    
    def _assess_severity(self, attack_type):
        """Assess severity of attack type"""
        severity_map = {
            "Port scanning": "Low",
            "SSH Brute Force": "High",
            "SQL Injection": "Critical",
            "RDP Brute Force": "High",
            "HTTP Attack": "Medium",
            "HTTPS Attack": "Medium",
            "DNS Amplification": "High",
            "MongoDB Exploit": "Critical"
        }
        return severity_map.get(attack_type, "Medium")

    def get_status(self):
        """Return current firewall status for dashboard"""
        # Calculate various statistics
        recent_attacks = [a for a in self.attack_log 
                         if datetime.fromisoformat(a['timestamp']) > datetime.now() - timedelta(minutes=10)]
        
        top_attacking_ips = sorted(
            [(ip, data['count'] if isinstance(data, dict) else data) 
             for ip, data in self.suspicious_ips.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        attack_types_count = {}
        for attack in self.attack_log[-50:]:  # Last 50 attacks
            attack_type = attack['type']
            if attack_type in attack_types_count:
                attack_types_count[attack_type] += 1
            else:
                attack_types_count[attack_type] = 1
        
        return {
            "open_ports": self.current_open_ports,
            "rotation_interval": self.rotation_interval,
            "attack_count": len(self.attack_log),
            "suspicious_ips": self.suspicious_ips,
            "recent_attacks": self.attack_log[-10:] if self.attack_log else [],
            "rotation_count": self.rotation_count,
            "port_history": self.port_history[-10:],
            "ip_shift_history": self.ip_shift_history[-10:],
            "monitoring": self.monitoring_data,
            "statistics": {
                "recent_attack_count": len(recent_attacks),
                "top_attacking_ips": top_attacking_ips,
                "attack_type_distribution": attack_types_count,
                "current_threat_level": self.monitoring_data["threat_level"]
            }
        }
    
    def get_historical_data(self, hours=24):
        """Get historical data for charts and analysis"""
        now = datetime.now()
        historical_data = {
            "threat_level_timeline": [],
            "attack_frequency": [],
            "port_changes": []
        }
        
        # Generate sample historical data (in real implementation, this would come from a database)
        for i in range(hours):
            time_point = now - timedelta(hours=i)
            historical_data["threat_level_timeline"].append({
                "timestamp": time_point.isoformat(),
                "level": random.randint(10, 80)
            })
            
            historical_data["attack_frequency"].append({
                "timestamp": time_point.isoformat(),
                "count": random.randint(0, 20)
            })
        
        return historical_data
    
    def simulate_attack(self, ip=None, port=None, attack_type=None):
        """Simulate an attack for testing purposes"""
        if ip is None:
            ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        
        if port is None:
            port = random.choice([p for p in self.ports if p not in self.current_open_ports])
        
        if attack_type is None:
            attack_type = self._classify_attack(port)
        
        self.log_attack(ip, port, attack_type)
        return {"ip": ip, "port": port, "type": attack_type}