"""
Phase/Anomaly Tracker Module — LUFT Framework
Detects dynamic couplings and emergent anomaly fields in simulated or real probe data.
Author: CarlDeanClineSr & Copilot
"""

import numpy as np
import pandas as pd

class DynamicCouplingField:
    """Represents a coupling constant promoted to a field (function of x, t)."""
    def __init__(self, base_value, spatial_variation=None, temporal_variation=None):
        self.base = base_value
        self.spatial_variation = spatial_variation  # Function or lambda: f(x)
        self.temporal_variation = temporal_variation  # Function or lambda: f(t)
    def value(self, x, t):
        val = self.base
        if self.spatial_variation:
            val *= self.spatial_variation(x)
        if self.temporal_variation:
            val *= self.temporal_variation(t)
        return val

class AnomalyField:
    """Tracks detected anomalies in space and time."""
    def __init__(self):
        self.events = []  # List of dicts: {'time': t, 'position': x, 'magnitude': m, 'type': 'phase_jump' etc.}
    def log_event(self, t, x, m, event_type="phase_jump"):
        self.events.append({'time': t, 'position': x, 'magnitude': m, 'type': event_type})
    def recent_events(self, dt=1.0):
        """Return events within last dt seconds."""
        now = self.events[-1]['time'] if self.events else 0
        return [e for e in self.events if now - e['time'] <= dt]

def detect_dynamic_anomalies(data, threshold=0.1, window=5):
    """
    Detects sudden parameter jumps (possible phase transitions) in lattice/probe data.
    data: pd.DataFrame with columns ['time', 'position', 'parameter']
    Returns: List of anomaly dicts.
    """
    anomalies = []
    for i in range(window, len(data)):
        prev = data['parameter'].iloc[i-window:i].mean()
        curr = data['parameter'].iloc[i]
        if abs(curr - prev) > threshold:
            anomalies.append({'time': data['time'].iloc[i], 
                              'position': data['position'].iloc[i], 
                              'magnitude': curr - prev,
                              'type': 'parameter_jump'})
    return anomalies

# Example usage (simulated data)
if __name__ == "__main__":
    # Simulate a parameter trace with an anomaly
    times = np.linspace(0, 100, 1001)
    positions = np.zeros_like(times)
    parameter = np.ones_like(times) * 1.0
    parameter[500:510] += 0.5  # insert anomaly
    df = pd.DataFrame({'time': times, 'position': positions, 'parameter': parameter})

    anomalies = detect_dynamic_anomalies(df, threshold=0.2)
    afield = AnomalyField()
    for a in anomalies:
        afield.log_event(a['time'], a['position'], a['magnitude'], a['type'])
    print("Detected Anomaly Events:", afield.events)
