import numpy as np

class PatternPredictor:
    def __init__(self):
        self.patterns = ['normal_day', 'peak_hours', 'weekend', 'attack']
    
    def predict(self, recent_traffic):
        if len(recent_traffic) < 5:
            return 'normal_day'
        
        # Simple heuristic prediction based on time
        from datetime import datetime
        hour = datetime.now().hour
        weekday = datetime.now().weekday()
        
        if weekday >= 5:
            return 'weekend'
        elif 9 <= hour <= 17:
            return 'peak_hours'
        else:
            return 'normal_day'