from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import time
import logging
from datetime import datetime, timedelta
import json
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'enhanced_hackathon_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global references to components
firewall = None
honeypot = None
traffic_generator = None
attack_simulator = None
start_time = time.time()

# Store historical data for analytics
historical_data = {
    "traffic": [],
    "threats": [],
    "performance": [],
    "firewall_events": [],
    "honeypot_events": []
}
MAX_HISTORY = 1000  # Maximum number of records to keep

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """API endpoint to get current system status"""
    status = get_system_status()
    return jsonify(status)

@app.route('/api/history')
def get_history():
    """API endpoint to get historical data"""
    timeframe = request.args.get('timeframe', '1h')  # 1h, 24h, 7d
    return jsonify(filter_history(timeframe))

@app.route('/api/traffic/start', methods=['POST'])
def start_traffic():
    """Start traffic generation"""
    data = request.get_json()
    intensity = data.get('intensity', 0.3) if data else 0.3
    traffic_type = data.get('type', 'mixed') if data else 'mixed'
    
    if traffic_generator:
        traffic_generator.start(intensity, traffic_type)
        log_event("traffic", f"Traffic generation started with intensity {intensity} and type {traffic_type}")
        return jsonify({"status": "started", "intensity": intensity, "type": traffic_type})
    
    return jsonify({"error": "Traffic generator not initialized"})

@app.route('/api/traffic/stop', methods=['POST'])
def stop_traffic():
    """Stop traffic generation"""
    if traffic_generator:
        traffic_generator.stop()
        log_event("traffic", "Traffic generation stopped")
        return jsonify({"status": "stopped"})
    
    return jsonify({"error": "Traffic generator not initialized"})

@app.route('/api/attack/start', methods=['POST'])
def start_attack():
    """Start attack simulation"""
    if attack_simulator:
        attack_thread = threading.Thread(target=attack_simulator.run_all_attacks, daemon=True)
        attack_thread.start()
        log_event("attack", "Attack simulation started")
        return jsonify({"status": "started"})
    
    return jsonify({"error": "Attack simulator not initialized"})

@app.route('/api/firewall/rules', methods=['GET', 'POST'])
def manage_firewall_rules():
    """Get or update firewall rules"""
    if not firewall:
        return jsonify({"error": "Firewall not initialized"})
    
    if request.method == 'GET':
        return jsonify({"rules": firewall.get_rules()})
    else:
        # Update rules
        data = request.get_json()
        if data and 'rules' in data:
            success = firewall.update_rules(data['rules'])
            if success:
                log_event("firewall", "Firewall rules updated")
                return jsonify({"status": "updated", "rules": firewall.get_rules()})
            else:
                return jsonify({"error": "Failed to update rules"})
        return jsonify({"error": "No rules provided"})

@app.route('/api/honeypot/config', methods=['GET', 'POST'])
def manage_honeypot_config():
    """Get or update honeypot configuration"""
    if not honeypot:
        return jsonify({"error": "Honeypot not initialized"})
    
    if request.method == 'GET':
        return jsonify({"config": honeypot.get_config()})
    else:
        # Update config
        data = request.get_json()
        if data and 'config' in data:
            success = honeypot.update_config(data['config'])
            if success:
                log_event("honeypot", "Honeypot configuration updated")
                return jsonify({"status": "updated", "config": honeypot.get_config()})
            else:
                return jsonify({"error": "Failed to update configuration"})
        return jsonify({"error": "No configuration provided"})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    client_id = request.sid
    logger.info(f"Client {client_id} connected to dashboard")
    
    # Send initial data
    emit_status()
    
    # Send historical data
    emit('historical_data', filter_history('1h'))

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    client_id = request.sid
    logger.info(f"Client {client_id} disconnected from dashboard")

@socketio.on('request_update')
def handle_update_request():
    """Handle manual update requests from client"""
    emit_status()

@socketio.on('request_config')
def handle_config_request(data):
    """Handle configuration requests from client"""
    component = data.get('component')
    if component == 'firewall':
        emit('firewall_config', {'rules': firewall.get_rules() if firewall else []})
    elif component == 'honeypot':
        emit('honeypot_config', {'config': honeypot.get_config() if honeypot else {}})

def get_system_status():
    """Get current system status"""
    status = {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "uptime": time.time() - start_time
        }
    }
    
    if firewall:
        firewall_status = firewall.get_status()
        firewall_status["rotation_count"] = getattr(firewall, "rotation_count", 0)
        firewall_status["port_history"] = getattr(firewall, "port_history", [])
        status["firewall"] = firewall_status
    
    if honeypot:
        honeypot_status = honeypot.get_stats()
        honeypot_status["total_attacks"] = len(getattr(honeypot, "attack_log", []))
        honeypot_status["recent_attacks"] = getattr(honeypot, "attack_log", [])[-10:] if hasattr(honeypot, "attack_log") and honeypot.attack_log else []
        honeypot_status["attack_types"] = get_attack_types_distribution()
        status["honeypot"] = honeypot_status
    
    if traffic_generator:
        traffic_status = traffic_generator.get_stats()
        traffic_status["total_traffic"] = getattr(traffic_generator, "total_traffic", 0)
        traffic_status["attack_traffic"] = getattr(traffic_generator, "attack_traffic", 0)
        traffic_status["normal_traffic"] = getattr(traffic_generator, "normal_traffic", 0)
        traffic_status["traffic_timeline"] = get_traffic_timeline()
        status["traffic"] = traffic_status
    
    # Add ML analysis data
    status["ml_analysis"] = get_ml_analysis()
    
    return status

def get_attack_types_distribution():
    """Get distribution of attack types from honeypot"""
    if not honeypot or not hasattr(honeypot, "attack_log"):
        return {"Port Scan": 0, "Brute Force": 0, "API Probing": 0}
    
    attack_types = {}
    for attack in honeypot.attack_log:
        attack_type = attack.get("type", "Unknown")
        attack_types[attack_type] = attack_types.get(attack_type, 0) + 1
    
    return attack_types

def get_traffic_timeline():
    """Generate traffic timeline data"""
    timeline = {}
    now = datetime.now()
    
    # Generate data for the last hour in 5-minute intervals
    for i in range(12):
        time_key = (now - timedelta(minutes=55 - i*5)).strftime("%H:%M")
        # Simulate traffic data
        timeline[time_key] = {
            "total": random.randint(50, 200),
            "attacks": random.randint(5, 50)
        }
    
    return timeline

def get_ml_analysis():
    """Generate ML analysis data"""
    threat_level = random.randint(10, 80)  # Simulate varying threat level
    
    patterns = []
    if threat_level > 50:
        patterns = ["Port scanning pattern detected", "Multiple failed login attempts"]
    elif threat_level > 30:
        patterns = ["Suspicious traffic pattern detected"]
    
    # Generate history for the threat level chart
    history = []
    now = datetime.now()
    for i in range(10):
        history.append({
            "timestamp": (now - timedelta(minutes=9-i)).isoformat(),
            "threat_level": random.randint(max(0, threat_level-20), min(100, threat_level+20)),
            "patterns": patterns if random.random() > 0.7 else []
        })
    
    return {
        "threat_level": threat_level,
        "patterns_detected": patterns,
        "history": history
    }

def emit_status():
    """Emit current status to all connected clients"""
    status = get_system_status()
    socketio.emit('status_update', status)
    
    # Store in history
    store_historical_data(status)

def store_historical_data(status):
    """Store current status in historical data"""
    timestamp = datetime.now().isoformat()
    
    # Store traffic data
    if 'traffic' in status:
        traffic_data = status['traffic'].copy()
        traffic_data['timestamp'] = timestamp
        historical_data['traffic'].append(traffic_data)
        
        # Keep only the most recent data
        if len(historical_data['traffic']) > MAX_HISTORY:
            historical_data['traffic'] = historical_data['traffic'][-MAX_HISTORY:]
    
    # Store threat data
    if 'honeypot' in status:
        threat_data = status['honeypot'].copy()
        threat_data['timestamp'] = timestamp
        historical_data['threats'].append(threat_data)
        
        if len(historical_data['threats']) > MAX_HISTORY:
            historical_data['threats'] = historical_data['threats'][-MAX_HISTORY:]
    
    # Store performance data
    performance_data = {
        'timestamp': timestamp,
        'cpu': random.randint(10, 80),  # Simulate CPU usage
        'memory': random.randint(30, 90),  # Simulate memory usage
        'network': status['traffic']['total_traffic'] if 'traffic' in status else 0
    }
    historical_data['performance'].append(performance_data)
    
    if len(historical_data['performance']) > MAX_HISTORY:
        historical_data['performance'] = historical_data['performance'][-MAX_HISTORY:]

def filter_history(timeframe):
    """Filter historical data based on timeframe"""
    now = datetime.now()
    filtered_data = {
        "traffic": [],
        "threats": [],
        "performance": []
    }
    
    # Calculate cutoff time based on timeframe
    if timeframe == '1h':
        cutoff = now.timestamp() - 3600
    elif timeframe == '24h':
        cutoff = now.timestamp() - 86400
    elif timeframe == '7d':
        cutoff = now.timestamp() - 604800
    else:
        cutoff = now.timestamp() - 3600  # Default to 1 hour
    
    # Filter traffic data
    for item in historical_data['traffic']:
        item_time = datetime.fromisoformat(item['timestamp']).timestamp()
        if item_time >= cutoff:
            filtered_data['traffic'].append(item)
    
    # Filter threat data
    for item in historical_data['threats']:
        item_time = datetime.fromisoformat(item['timestamp']).timestamp()
        if item_time >= cutoff:
            filtered_data['threats'].append(item)
    
    # Filter performance data
    for item in historical_data['performance']:
        item_time = datetime.fromisoformat(item['timestamp']).timestamp()
        if item_time >= cutoff:
            filtered_data['performance'].append(item)
    
    return filtered_data

def log_event(event_type, message):
    """Log an event and notify clients"""
    event = {
        "type": event_type,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    logger.info(f"{event_type.upper()}: {message}")
    socketio.emit('event', event)

def status_updater():
    """Background thread to update dashboard status periodically"""
    while True:
        time.sleep(3)  # Update every 3 seconds
        try:
            emit_status()
        except Exception as e:
            logger.error(f"Error in status updater: {e}")

def start_dashboard(firewall_instance, honeypot_instance, attack_simulator_instance, host='0.0.0.0', port=5000):
    """Start the dashboard with component references"""
    global firewall, honeypot, traffic_generator, attack_simulator, start_time
    
    firewall = firewall_instance
    honeypot = honeypot_instance
    attack_simulator = attack_simulator_instance
    start_time = time.time()
    
    # Set socketio references for components
    if firewall and hasattr(firewall, 'socketio'):
        firewall.socketio = socketio
    if firewall and hasattr(firewall, 'log_event'):
        firewall.log_event = log_event
    
    if honeypot and hasattr(honeypot, 'socketio'):
        honeypot.socketio = socketio
    if honeypot and hasattr(honeypot, 'log_event'):
        honeypot.log_event = log_event
    
    # Initialize traffic generator if not provided
    if not traffic_generator:
        traffic_generator = AITrafficGenerator(socketio, log_event)
    
    # Start background updater thread
    updater_thread = threading.Thread(target=status_updater, daemon=True)
    updater_thread.start()
    
    logger.info(f"Starting enhanced dashboard on {host}:{port}")
    socketio.run(app, host=host, port=port, debug=False, use_reloader=False)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# Enhanced AITrafficGenerator class with actual traffic generation
class AITrafficGenerator:
    def __init__(self, socketio=None, log_event=None):
        self.socketio = socketio
        self.log_event = log_event
        self.running = False
        self.total_traffic = 0
        self.attack_traffic = 0
        self.normal_traffic = 0
        self.intensity = 0.3
        self.traffic_type = 'mixed'
        self.traffic_thread = None
        self.stop_event = threading.Event()
        
    def start(self, intensity=0.3, traffic_type='mixed'):
        self.running = True
        self.intensity = intensity
        self.traffic_type = traffic_type
        self.stop_event.clear()
        
        # Start traffic generation in a separate thread
        self.traffic_thread = threading.Thread(target=self._generate_traffic, daemon=True)
        self.traffic_thread.start()
        
        if self.log_event:
            self.log_event("traffic", f"Traffic generation started with intensity {intensity}")
        
    def stop(self):
        self.running = False
        self.stop_event.set()
        if self.traffic_thread:
            self.traffic_thread.join(timeout=1.0)
        if self.log_event:
            self.log_event("traffic", "Traffic generation stopped")
            
    def _generate_traffic(self):
        """Background thread to generate traffic data"""
        while self.running and not self.stop_event.is_set():
            try:
                # Generate traffic based on intensity
                traffic_amount = random.randint(10, 100) * self.intensity
                self.total_traffic += traffic_amount
                
                # Determine if this is attack traffic based on type
                if self.traffic_type == 'attack':
                    self.attack_traffic += traffic_amount
                elif self.traffic_type == 'normal':
                    self.normal_traffic += traffic_amount
                else:  # mixed traffic
                    if random.random() < 0.2:  # 20% chance of attack traffic
                        self.attack_traffic += traffic_amount
                    else:
                        self.normal_traffic += traffic_amount
                
                # Sleep for a bit before generating more traffic
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in traffic generation: {e}")
                break
            
    def get_stats(self):
        return {
            "running": self.running,
            "intensity": self.intensity,
            "type": self.traffic_type,
            "total_traffic": self.total_traffic,
            "attack_traffic": self.attack_traffic,
            "normal_traffic": self.normal_traffic
        }

if __name__ == '__main__':
    # For testing without external components
    class MockComponent:
        def __init__(self):
            self.rotation_count = 15
            self.port_history = [
                {"timestamp": (datetime.now() - timedelta(minutes=10)).isoformat(), "ports": [80, 443, 22]},
                {"timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(), "ports": [443, 8080, 3389]}
            ]
            self.attack_log = [
                {"timestamp": (datetime.now() - timedelta(minutes=2)).isoformat(), "ip": "192.168.1.5", "type": "Port Scan", "details": "Attempted connection to port 22"},
                {"timestamp": (datetime.now() - timedelta(minutes=1)).isoformat(), "ip": "10.0.0.8", "type": "Brute Force", "details": "Multiple login attempts"}
            ]
            
        def get_status(self):
            return {
                "open_ports": [80, 443, 8080],
                "rotation_interval": 30,
                "attack_count": 12,
                "suspicious_ips": {"192.168.1.5": 3, "10.0.0.8": 2},
                "rotation_count": self.rotation_count,
                "port_history": self.port_history
            }
        
        def get_stats(self):
            return {
                "total_attacks": 7,
                "recent_attacks": self.attack_log[-10:],
                "attack_types": {"Port Scan": 4, "Brute Force": 3}
            }
        
        def get_rules(self):
            return ["Allow HTTP", "Block SSH", "Allow HTTPS"]
        
        def get_config(self):
            return {"mode": "advanced", "sensitivity": "high"}
        
        def update_rules(self, rules):
            return True
        
        def update_config(self, config):
            return True
    
    # Initialize the traffic generator
    traffic_generator = AITrafficGenerator(socketio, log_event)
    
    # Start the dashboard with mock components
    start_dashboard(MockComponent(), MockComponent(), None, host='localhost', port=5000)