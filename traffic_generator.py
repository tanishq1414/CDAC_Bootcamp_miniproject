import numpy as np
import random
import time
import threading
import logging
from datetime import datetime
from app.config import Config

class AITrafficGenerator:
    def __init__(self, dashboard_callback=None):
        self.dashboard_callback = dashboard_callback
        self.logger = logging.getLogger("AITraffic")
        self.running = False
        
        self.traffic_patterns = {
            'normal_day': self.generate_normal_day_traffic,
            'peak_hours': self.generate_peak_hours_traffic,
            'weekend': self.generate_weekend_traffic,
            'attack': self.generate_attack_traffic
        }
        
        self.current_pattern = 'normal_day'
        self.stats = {
            'total_requests_generated': 0,
            'current_pattern': self.current_pattern,
            'pattern_changes': 0,
            'anomalies_detected': 0,
            'last_anomaly': None
        }
    
    def generate_normal_day_traffic(self):
        features = [
            random.uniform(10, 50), random.uniform(0.1, 0.3),
            random.uniform(1, 5), random.uniform(0.2, 0.4)
        ]
        
        urls = ["/", "/about", "/contact", "/products", "/services"]
        weights = [0.3, 0.1, 0.08, 0.15, 0.12]
        
        for _ in range(int(features[0])):
            url = random.choices(urls, weights=weights)[0]
            self._make_request(url)
            time.sleep(random.uniform(0.1, 0.5))
        
        return features
    
    def generate_peak_hours_traffic(self):
        features = [
            random.uniform(80, 200), random.uniform(0.05, 0.15),
            random.uniform(2, 8), random.uniform(0.3, 0.5)
        ]
        
        urls = ["/", "/products", "/services", "/api/data", "/checkout"]
        weights = [0.25, 0.2, 0.15, 0.1, 0.08]
        
        for _ in range(int(features[0])):
            url = random.choices(urls, weights=weights)[0]
            self._make_request(url)
            time.sleep(random.uniform(0.05, 0.2))
        
        return features
    
    def generate_weekend_traffic(self):
        features = [
            random.uniform(30, 100), random.uniform(0.08, 0.2),
            random.uniform(1.5, 6), random.uniform(0.4, 0.6)
        ]
        
        urls = ["/", "/blog", "/gallery", "/events", "/promotions"]
        weights = [0.35, 0.2, 0.15, 0.1, 0.08]
        
        for _ in range(int(features[0])):
            url = random.choices(urls, weights=weights)[0]
            self._make_request(url)
            time.sleep(random.uniform(0.2, 1.0))
        
        return features
    
    def generate_attack_traffic(self):
        features = [
            random.uniform(200, 1000), random.uniform(0.3, 0.8),
            random.uniform(5, 20), random.uniform(0.8, 0.95)
        ]
        
        suspicious_urls = ["/admin", "/wp-admin", "/phpmyadmin", "/config.json"]
        
        for _ in range(int(features[0] / 10)):
            url = random.choice(suspicious_urls)
            self._make_request(url, suspicious=True)
            time.sleep(random.uniform(0.01, 0.1))
        
        return features
    
    def _make_request(self, url, suspicious=False):
        try:
            import requests
            headers = {
                'User-Agent': random.choice([
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15'
                ])
            }
            
            if suspicious:
                headers['X-Forwarded-For'] = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            
            response = requests.get(f"http://127.0.0.1:8081{url}", headers=headers, timeout=5)
            
            self.stats['total_requests_generated'] += 1
            
            if self.dashboard_callback:
                self.dashboard_callback('ai_traffic_request', {
                    'url': url,
                    'status': response.status_code,
                    'suspicious': suspicious,
                    'total_requests': self.stats['total_requests_generated']
                })
            
            return response.status_code
            
        except Exception as e:
            self.logger.error(f"Request failed: {e}")
            return None
    
    def adapt_pattern(self):
        current_hour = datetime.now().hour
        current_weekday = datetime.now().weekday()
        
        if current_weekday >= 5:
            new_pattern = 'weekend'
        elif 9 <= current_hour <= 17:
            new_pattern = 'peak_hours'
        else:
            new_pattern = 'normal_day'
        
        if random.random() < 0.05:
            new_pattern = 'attack'
        
        if new_pattern != self.current_pattern:
            self.current_pattern = new_pattern
            self.stats['current_pattern'] = new_pattern
            self.stats['pattern_changes'] += 1
            
            self.logger.info(f"Traffic pattern changed to: {new_pattern}")
            
            if self.dashboard_callback:
                self.dashboard_callback('pattern_change', {
                    'new_pattern': new_pattern,
                    'total_changes': self.stats['pattern_changes']
                })
    
    def generate_traffic(self):
        while self.running:
            self.adapt_pattern()
            self.traffic_patterns[self.current_pattern]()
            time.sleep(60)
    
    def start(self):
        self.running = True
        self.logger.info("Starting AI Traffic Generator")
        
        traffic_thread = threading.Thread(target=self.generate_traffic, daemon=True)
        traffic_thread.start()
    
    def stop(self):
        self.running = False
        self.logger.info("Stopping AI Traffic Generator")
    
    def get_stats(self):
        return self.stats