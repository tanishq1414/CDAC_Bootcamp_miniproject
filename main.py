import threading
import time
import logging
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import random
from datetime import datetime, timedelta
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("firewall.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hackathon_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
class SystemState:
    def __init__(self):
        self.firewall = {
            "open_ports": [80, 443, 8080],
            "rotation_interval": 30,
            "attack_count": 0,
            "suspicious_ips": {},
            "rotation_count": 0,
            "port_history": [],
            "ip_shift_history": []
        }
        
        self.honeypot = {
            "total_attacks": 0,
            "recent_attacks": [],
            "attack_types": {},
            "attack_timeline": self._init_timeline()
        }
        
        self.traffic = {
            "total_traffic": 0,
            "attack_traffic": 0,
            "normal_traffic": 0,
            "traffic_timeline": self._init_timeline(),
            "ip_activity": {}
        }
        
        self.ml_analysis = {
            "threat_level": 0,
            "patterns_detected": [],
            "history": [],
            "threat_timeline": self._init_timeline()
        }
        
        self.monitoring = {
            "live_threats": [],
            "ip_shift_data": [],
            "attack_patterns": [],
            "real_time_graphs": {
                "threat_level": [],
                "traffic_volume": [],
                "attack_frequency": []
            }
        }
    
    def _init_timeline(self):
        """Initialize empty timeline for the last hour"""
        timeline = {}
        now = datetime.now()
        for i in range(12):
            time_key = (now - timedelta(minutes=55 - i*5)).strftime("%H:%M")
            timeline[time_key] = 0
        return timeline

# Create instances
state = SystemState()
ports = [80, 443, 8080, 8443, 22, 3389, 21, 25, 53]
attack_types = ["Port Scan", "Brute Force", "SQL Injection", "XSS", "DDoS", "Phishing", "Malware"]
ip_pool = [f"192.168.1.{i}" for i in range(1, 50)] + [f"10.0.0.{i}" for i in range(1, 50)]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify({
        "firewall": state.firewall,
        "honeypot": state.honeypot,
        "traffic": state.traffic,
        "ml_analysis": state.ml_analysis,
        "monitoring": state.monitoring
    })

@app.route('/api/traffic/start', methods=['POST'])
def start_traffic():
    # Start attack simulation in background
    attack_thread = threading.Thread(target=run_attacks, daemon=True)
    attack_thread.start()
    return jsonify({"status": "started", "message": "Traffic generation started"})

@app.route('/api/traffic/stop', methods=['POST'])
def stop_traffic():
    # In a real implementation, you would stop the attack simulation
    return jsonify({"status": "stopped", "message": "Traffic generation stopped"})

@socketio.on('connect')
def handle_connect():
    logger.info("Client connected to dashboard")
    socketio.emit('status_update', get_status().json)

def run_attacks():
    """Run attack simulations in the background"""
    while True:
        try:
            # Simulate port scanning
            simulate_port_scan()
            time.sleep(random.uniform(5, 15))
            
            # Simulate brute force attacks
            if random.random() < 0.7:
                simulate_brute_force()
                time.sleep(random.uniform(3, 10))
            
            # Simulate API probing
            if random.random() < 0.5:
                simulate_api_probing()
                time.sleep(random.uniform(2, 8))
                
        except Exception as e:
            logger.error(f"Error in attack simulation: {e}")
            time.sleep(10)

def simulate_port_scan():
    """Simulate port scanning activity"""
    target_ports = random.sample(ports, random.randint(3, 6))
    source_ip = random.choice(ip_pool)
    
    for port in target_ports:
        if port not in state.firewall["open_ports"]:
            # This is an attack on a closed port
            attack_type = "Port Scan"
            simulate_attack(source_ip, port, attack_type)
        time.sleep(0.2)

def simulate_brute_force():
    """Simulate brute force attacks"""
    source_ip = random.choice(ip_pool)
    target_port = random.choice([22, 3389, 21])  # Common brute force targets
    
    if target_port not in state.firewall["open_ports"]:
        for i in range(random.randint(3, 8)):
            attack_type = "Brute Force"
            simulate_attack(source_ip, target_port, attack_type)
            time.sleep(0.5)

def simulate_api_probing():
    """Simulate API endpoint probing"""
    source_ip = random.choice(ip_pool)
    target_port = random.choice([80, 443, 8080])
    
    if target_port not in state.firewall["open_ports"]:
        attack_type = random.choice(["SQL Injection", "XSS", "API Probe"])
        for i in range(random.randint(2, 5)):
            simulate_attack(source_ip, target_port, attack_type)
            time.sleep(0.3)

def firewall_rotation():
    """Simulate firewall port rotation and monitoring"""
    while True:
        time.sleep(state.firewall["rotation_interval"])
        
        # Store current state in history
        timestamp = datetime.now().isoformat()
        state.firewall["port_history"].append({
            "timestamp": timestamp,
            "ports": state.firewall["open_ports"].copy()
        })
        
        # Keep only last 20 history entries
        if len(state.firewall["port_history"]) > 20:
            state.firewall["port_history"] = state.firewall["port_history"][-20:]
        
        # Rotate ports
        current_ports = state.firewall["open_ports"].copy()
        
        # Close 1-2 ports
        ports_to_close = min(2, len(current_ports))
        for _ in range(ports_to_close):
            if current_ports:
                port = random.choice(current_ports)
                current_ports.remove(port)
        
        # Open 1-2 new ports
        ports_to_open = random.randint(1, 2)
        for _ in range(ports_to_open):
            available_ports = [p for p in ports if p not in current_ports]
            if available_ports:
                new_port = random.choice(available_ports)
                current_ports.append(new_port)
        
        # Ensure we always have at least 2 ports open
        while len(current_ports) < 2:
            available_ports = [p for p in ports if p not in current_ports]
            if available_ports:
                new_port = random.choice(available_ports)
                current_ports.append(new_port)
        
        state.firewall["open_ports"] = current_ports
        state.firewall["rotation_count"] += 1
        
        # Record IP shift
        state.firewall["ip_shift_history"].append({
            "timestamp": timestamp,
            "ip_count": len(state.firewall["suspicious_ips"]),
            "new_ips": random.randint(0, 3)
        })
        
        if len(state.firewall["ip_shift_history"]) > 15:
            state.firewall["ip_shift_history"] = state.firewall["ip_shift_history"][-15:]
        
        # Update ML analysis
        update_ml_analysis()
        
        # Update monitoring data
        update_monitoring_data()
        
        # Emit update to all clients
        socketio.emit('status_update', get_status().json)

def simulate_attack(ip, port, attack_type):
    """Simulate a cyber attack"""
    # Update firewall stats
    state.firewall["attack_count"] += 1
    if ip in state.firewall["suspicious_ips"]:
        state.firewall["suspicious_ips"][ip] += 1
    else:
        state.firewall["suspicious_ips"][ip] = 1
    
    # Update honeypot stats
    state.honeypot["total_attacks"] += 1
    attack_entry = {
        "timestamp": datetime.now().isoformat(),
        "ip": ip,
        "type": attack_type,
        "details": f"Attempted {attack_type} on port {port}",
        "target": f"Port {port}",
        "severity": random.choice(["Low", "Medium", "High", "Critical"])
    }
    state.honeypot["recent_attacks"].append(attack_entry)
    
    # Keep only recent attacks
    if len(state.honeypot["recent_attacks"]) > 15:
        state.honeypot["recent_attacks"] = state.honeypot["recent_attacks"][-15:]
    
    # Update attack types
    if attack_type in state.honeypot["attack_types"]:
        state.honeypot["attack_types"][attack_type] += 1
    else:
        state.honeypot["attack_types"][attack_type] = 1
    
    # Update traffic stats
    state.traffic["total_traffic"] += 1
    state.traffic["attack_traffic"] += 1
    
    # Update IP activity
    if ip in state.traffic["ip_activity"]:
        state.traffic["ip_activity"][ip] += 1
    else:
        state.traffic["ip_activity"][ip] = 1
    
    # Update timeline
    update_timeline(True)
    
    # Add to live threats
    state.monitoring["live_threats"].append({
        "timestamp": datetime.now().isoformat(),
        "ip": ip,
        "type": attack_type,
        "severity": attack_entry["severity"]
    })
    
    if len(state.monitoring["live_threats"]) > 10:
        state.monitoring["live_threats"] = state.monitoring["live_threats"][-10:]
    
    # Emit individual events
    socketio.emit('firewall_attack', attack_entry)
    socketio.emit('honeypot_attack', attack_entry)
    socketio.emit('live_threat', state.monitoring["live_threats"][-1])

def update_timeline(is_attack=False):
    """Update traffic timeline"""
    current_time = datetime.now()
    minute = int(current_time.strftime("%M"))
    rounded_minute = (minute // 5) * 5
    time_key = current_time.replace(minute=rounded_minute).strftime("%H:%M")
    
    # Update traffic timeline
    if time_key in state.traffic["traffic_timeline"]:
        state.traffic["traffic_timeline"][time_key] += 1
    else:
        state.traffic["traffic_timeline"][time_key] = 1
    
    # Update attack timeline
    if is_attack:
        if time_key in state.honeypot["attack_timeline"]:
            state.honeypot["attack_timeline"][time_key] += 1
        else:
            state.honeypot["attack_timeline"][time_key] = 1
    
    # Keep only last 12 time slots (1 hour)
    for timeline in [state.traffic["traffic_timeline"], state.honeypot["attack_timeline"]]:
        if len(timeline) > 12:
            # Remove oldest entry
            oldest_key = sorted(timeline.keys())[0]
            del timeline[oldest_key]

def update_ml_analysis():
    """Simulate ML analysis"""
    # Calculate threat level based on recent activity
    base_threat = min(100, state.firewall["attack_count"] * 2 + len(state.firewall["suspicious_ips"]) * 3)
    threat_change = random.randint(-5, 10)
    state.ml_analysis["threat_level"] = max(0, min(100, base_threat + threat_change))
    
    # Update threat timeline
    current_time = datetime.now()
    minute = int(current_time.strftime("%M"))
    rounded_minute = (minute // 5) * 5
    time_key = current_time.replace(minute=rounded_minute).strftime("%H:%M")
    
    if time_key in state.ml_analysis["threat_timeline"]:
        state.ml_analysis["threat_timeline"][time_key] = state.ml_analysis["threat_level"]
    else:
        state.ml_analysis["threat_timeline"][time_key] = state.ml_analysis["threat_level"]
    
    if len(state.ml_analysis["threat_timeline"]) > 12:
        oldest_key = sorted(state.ml_analysis["threat_timeline"].keys())[0]
        del state.ml_analysis["threat_timeline"][oldest_key]
    
    # Occasionally detect new patterns
    patterns = [
        "Port scanning pattern detected",
        "Possible brute force attempt",
        "SQL injection characteristics found",
        "DDoS amplification pattern",
        "Geographical anomaly in requests",
        "Unusual traffic spike detected",
        "Suspicious user agent patterns"
    ]
    
    if random.random() < 0.4 and patterns and state.ml_analysis["threat_level"] > 30:
        new_pattern = random.choice(patterns)
        if new_pattern not in state.ml_analysis["patterns_detected"]:
            state.ml_analysis["patterns_detected"].append(new_pattern)
            if len(state.ml_analysis["patterns_detected"]) > 5:
                state.ml_analysis["patterns_detected"].pop(0)
    
    # Add to history
    analysis_entry = {
        "timestamp": datetime.now().isoformat(),
        "threat_level": state.ml_analysis["threat_level"],
        "patterns": state.ml_analysis["patterns_detected"].copy()
    }
    state.ml_analysis["history"].append(analysis_entry)
    
    # Keep only recent history
    if len(state.ml_analysis["history"]) > 10:
        state.ml_analysis["history"] = state.ml_analysis["history"][-10:]
    
    socketio.emit('ml_update', state.ml_analysis)

def update_monitoring_data():
    """Update real-time monitoring data for graphs"""
    current_time = datetime.now().isoformat()
    
    # Update real-time graph data
    state.monitoring["real_time_graphs"]["threat_level"].append({
        "time": current_time,
        "value": state.ml_analysis["threat_level"]
    })
    
    state.monitoring["real_time_graphs"]["traffic_volume"].append({
        "time": current_time,
        "value": state.traffic["total_traffic"] % 100  # Simulate fluctuating traffic
    })
    
    state.monitoring["real_time_graphs"]["attack_frequency"].append({
        "time": current_time,
        "value": state.honeypot["total_attacks"] % 20  # Simulate attack frequency
    })
    
    # Keep only recent data for graphs
    for graph in state.monitoring["real_time_graphs"].values():
        if len(graph) > 15:
            graph.pop(0)
    
    # Update IP shift data
    if state.firewall["ip_shift_history"]:
        state.monitoring["ip_shift_data"] = state.firewall["ip_shift_history"][-10:]
    
    # Update attack patterns
    state.monitoring["attack_patterns"] = [
        {"type": atype, "count": count} 
        for atype, count in state.honeypot["attack_types"].items()
    ]
    
    socketio.emit('monitoring_update', state.monitoring)

def simulate_normal_traffic():
    """Simulate normal traffic patterns"""
    while True:
        time.sleep(random.uniform(2, 8))
        
        # Simulate normal traffic
        state.traffic["total_traffic"] += 1
        state.traffic["normal_traffic"] += 1
        update_timeline(False)
        
        # Update monitoring occasionally
        if random.random() < 0.3:
            update_monitoring_data()
            socketio.emit('status_update', get_status().json)

def continuous_monitoring():
    """Continuous monitoring updates for real-time graphs"""
    while True:
        time.sleep(2)  # Update every 2 seconds
        update_monitoring_data()
        socketio.emit('monitoring_update', state.monitoring)

def start_dashboard():
    # Start firewall rotation in background
    rotation_thread = threading.Thread(target=firewall_rotation, daemon=True)
    rotation_thread.start()
    
    # Start traffic simulation in background
    traffic_thread = threading.Thread(target=simulate_normal_traffic, daemon=True)
    traffic_thread.start()
    
    # Start monitoring updates
    monitoring_thread = threading.Thread(target=continuous_monitoring, daemon=True)
    monitoring_thread.start()
    
    logger.info("Starting dashboard on localhost:5000")
    socketio.run(app, host='127.0.0.1', port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    start_dashboard()