import numpy as np
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.is_trained = False
    
    def train(self, X):
        self.model.fit(X)
        self.is_trained = True
    
    def detect_anomalies(self, X):
        if not self.is_trained:
            raise Exception("Model not trained yet")
        return self.model.predict(X)
    
    def is_anomaly(self, x):
        return self.detect_anomalies([x])[0] == -1