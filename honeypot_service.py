from flask import Flask, request, jsonify, render_template_string
from cryptography.fernet import Fernet
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# HTML template for fake login page
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Secure Corporate Portal</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .login-box { background: white; padding: 20px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); max-width: 400px; margin: auto; }
        input[type=text], input[type=password] { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 3px; }
        input[type=submit] { background: #0066cc; color: white; border: none; padding: 10px 15px; border-radius: 3px; cursor: pointer; }
        .alert { color: #d9534f; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Secure Corporate Portal</h2>
        {% if error %}
        <p class="alert">{{ error }}</p>
        {% endif %}
        <form method="post">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <input type="submit" value="Login">
        </form>
    </div>
</body>
</html>
"""

class HoneypotService:
    def __init__(self, socketio=None):
        self.app = Flask(__name__)
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.attack_log = []
        self.socketio = socketio
        self.setup_routes()
    
    def setup_routes(self):
        """Setup honeypot routes"""
        @self.app.route('/', methods=['GET', 'POST'])
        def fake_login():
            client_ip = request.remote_addr
            if request.method == 'POST':
                username = request.form.get('username', '')
                password = request.form.get('password', '')
                
                # Encrypt and store the credentials (fake)
                fake_data = {
                    "username": username,
                    "password": password,
                    "timestamp": datetime.now().isoformat(),
                    "user_agent": request.headers.get('User-Agent', ''),
                    "client_ip": client_ip
                }
                
                encrypted_data = self.encrypt_data(json.dumps(fake_data))
                
                # Log the attempt
                self.log_attack(client_ip, "Credential harvesting", 
                               f"Username: {username}, Password: {password}")
                
                # Return a fake error to keep the attacker engaged
                return render_template_string(LOGIN_TEMPLATE, 
                                            error="Invalid credentials. Please try again.")
            
            self.log_attack(client_ip, "Port scanning", "Accessed honeypot login page")
            return render_template_string(LOGIN_TEMPLATE)
        
        @self.app.route('/api/users', methods=['GET'])
        def fake_api():
            client_ip = request.remote_addr
            self.log_attack(client_ip, "API probing", "Attempted to access user API")
            
            # Return fake encrypted data that looks like real user data
            fake_users = [
                {"id": 101, "name": "admin", "email": "admin@company.com", "role": "Administrator"},
                {"id": 102, "name": "j.smith", "email": "j.smith@company.com", "role": "Developer"},
                {"id": 103, "name": "s.johnson", "email": "s.johnson@company.com", "role": "Manager"}
            ]
            
            # Encrypt the fake data
            encrypted_data = self.encrypt_data(json.dumps(fake_users))
            return jsonify({"data": encrypted_data, "status": "success"})
        
        @self.app.route('/admin', methods=['GET'])
        def fake_admin():
            client_ip = request.remote_addr
            self.log_attack(client_ip, "Admin portal access", "Attempted to access admin portal")
            return "Access denied. Insufficient privileges.", 403
    
    def encrypt_data(self, data):
        """Encrypt data to make it look legitimate"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def log_attack(self, ip, attack_type, details):
        """Log attack attempts to the honeypot"""
        attack_entry = {
            "timestamp": datetime.now().isoformat(),
            "ip": ip,
            "type": attack_type,
            "details": details
        }
        self.attack_log.append(attack_entry)
        logger.warning(f"Honeypot attack: {attack_type} from {ip} - {details}")
        
        # Notify dashboard of the new attack
        if self.socketio:
            self.socketio.emit('honeypot_attack', attack_entry)
            self.socketio.emit('honeypot_update', self.get_stats())
    
    def start(self):
        """Start the honeypot service"""
        logger.info("Starting honeypot service on port 8080")
        self.app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
    
    def get_stats(self):
        """Return honeypot statistics for dashboard"""
        return {
            "total_attacks": len(self.attack_log),
            "recent_attacks": self.attack_log[-10:] if self.attack_log else [],
            "attack_types": self._count_attack_types()
        }
    
    def _count_attack_types(self):
        """Count occurrences of each attack type"""
        types = {}
        for attack in self.attack_log:
            if attack["type"] in types:
                types[attack["type"]] += 1
            else:
                types[attack["type"]] = 1
        return types