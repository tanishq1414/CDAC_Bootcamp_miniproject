import random
import time
import threading
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class MLSecurityAnalyzer:
    def __init__(self, socketio=None):
        self.socketio = socketio
        self.is_running = False
        self.analysis_thread = None
        self.threat_level = 0  # 0-100 scale
        self.patterns_detected = []
        self.analysis_history = []
        
    def start_analysis(self):
        """Start the ML-like security analysis"""
        if self.is_running:
            return
            
        self.is_running = True
        self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        self.analysis_thread.start()
        logger.info("ML Security Analyzer started")
    
    def stop_analysis(self):
        """Stop the analysis"""
        self.is_running = False
        logger.info("ML Security Analyzer stopped")
    
    def _analysis_loop(self):
        """Main analysis loop that simulates ML behavior"""
        while self.is_running:
            # Simulate ML analysis by generating random insights
            self._generate_insights()
            
            # Update dashboard
            if self.socketio:
                self.socketio.emit('ml_update', self.get_status())
            
            time.sleep(10)  # Analyze every 10 seconds
    
    def _generate_insights(self):
        """Generate simulated ML insights"""
        # Randomly adjust threat level
        change = random.randint(-5, 10)
        self.threat_level = max(0, min(100, self.threat_level + change))
        
        # Detect some random patterns
        patterns = [
            "Port scanning pattern detected",
            "Possible brute force attempt",
            "SQL injection characteristics found",
            "DDoS amplification pattern",
            "Geographical anomaly in requests",
            "Unusual request frequency",
            "Suspicious user agent pattern"
        ]
        
        if random.random() < 0.3:  # 30% chance to detect a pattern
            new_pattern = random.choice(patterns)
            if new_pattern not in self.patterns_detected:
                self.patterns_detected.append(new_pattern)
                # Keep only recent patterns
                if len(self.patterns_detected) > 5:
                    self.patterns_detected.pop(0)
        
        # Log this analysis cycle
        analysis_entry = {
            "timestamp": datetime.now().isoformat(),
            "threat_level": self.threat_level,
            "patterns": self.patterns_detected.copy()
        }
        self.analysis_history.append(analysis_entry)
        
        # Keep only recent history
        if len(self.analysis_history) > 20:
            self.analysis_history = self.analysis_history[-20:]
    
    def analyze_request(self, request_data):
        """Analyze a single request (simulated ML analysis)"""
        # Simple heuristic-based analysis (simulating ML)
        score = 0
        
        # Check for suspicious characteristics
        if len(request_data.get('path', '')) > 100:
            score += 20  # Long URLs are suspicious
            
        if request_data.get('method') == 'POST' and len(request_data.get('params', {})) > 10:
            score += 15  # Many parameters in POST
            
        if 'sql' in request_data.get('path', '').lower() or 'union' in request_data.get('path', '').lower():
            score += 30  # SQL-related keywords
            
        if 'script' in request_data.get('path', '').lower() or 'alert' in request_data.get('path', '').lower():
            score += 25  # XSS-related keywords
            
        return min(100, score)
    
    def get_status(self):
        """Get current analysis status"""
        return {
            "threat_level": self.threat_level,
            "patterns_detected": self.patterns_detected,
            "history": self.analysis_history[-10:] if self.analysis_history else []
        }