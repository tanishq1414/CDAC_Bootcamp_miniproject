import requests
import time
import random
import threading
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AttackSimulator:
    def __init__(self, target_url="http://localhost:8080"):
        self.target_url = target_url
        self.attack_log = []
    
    def simulate_port_scan(self):
        """Simulate a port scanning attack"""
        ports = [80, 443, 8080, 8443, 21, 22, 23, 25, 53, 110, 135, 139, 143, 445, 993, 995, 1723, 3306, 3389, 5900, 8081]
        
        for port in ports:
            try:
                # Try to connect to various ports
                url = f"http://localhost:{port}"
                response = requests.get(url, timeout=1)
                self.log_attack(f"Port {port} is open - Response: {response.status_code}")
            except:
                # Port is closed or not responding
                self.log_attack(f"Port {port} is closed/filtered")
            
            time.sleep(0.5)  # Be somewhat stealthy
    
    def simulate_brute_force(self):
        """Simulate a brute force login attempt"""
        usernames = ["admin", "root", "administrator", "test", "user"]
        passwords = ["password", "123456", "admin", "test", "root", "welcome", "123456789"]
        
        for username in usernames:
            for password in passwords:
                try:
                    response = requests.post(
                        f"{self.target_url}/",
                        data={"username": username, "password": password},
                        timeout=2
                    )
                    self.log_attack(f"Login attempt: {username}/{password} - Status: {response.status_code}")
                except Exception as e:
                    self.log_attack(f"Login attempt failed: {str(e)}")
                
                time.sleep(0.3)
    
    def simulate_api_probing(self):
        """Simulate API endpoint probing"""
        endpoints = ["/api/users", "/api/admin", "/api/config", "/api/database", "/api/backup"]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.target_url}{endpoint}", timeout=2)
                self.log_attack(f"API probe: {endpoint} - Status: {response.status_code}")
            except Exception as e:
                self.log_attack(f"API probe failed: {endpoint} - Error: {str(e)}")
            
            time.sleep(0.5)
    
    def log_attack(self, message):
        """Log attack simulation activity"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.attack_log.append(log_entry)
        logger.info(f"Attack simulation: {message}")
        print(log_entry)
    
    def run_all_attacks(self):
        """Run all attack simulations"""
        print("Starting attack simulations...")
        
        # Run attacks in separate threads to simulate multiple attackers
        threads = [
            threading.Thread(target=self.simulate_port_scan),
            threading.Thread(target=self.simulate_brute_force),
            threading.Thread(target=self.simulate_api_probing)
        ]
        
        for thread in threads:
            thread.start()
            time.sleep(1)  # Stagger the starts
        
        for thread in threads:
            thread.join()
        
        print("All attack simulations completed.")

if __name__ == "__main__":
    simulator = AttackSimulator()
    simulator.run_all_attacks()