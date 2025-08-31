# AMD-Hardware-Competition-2025/redpitaya/sensor_simulation.py

import numpy as np
import time
import math
import random

class RULSensorSimulator:
    """
    Simulates sensor data for Remaining Useful Life (RUL) prediction
    Shows progressive machine degradation over 3 minutes (180 seconds)
    """
    
    def __init__(self, duration=180, sampling_rate=1.0):
        """
        Initialize the RUL simulator
        :param duration: Total simulation time in seconds (default: 3 minutes)
        :param sampling_rate: Samples per second (default: 1 Hz)
        """
        self.duration = duration
        self.sampling_rate = sampling_rate
        self.total_samples = int(duration * sampling_rate)
        self.current_sample = 0
        
        # Define degradation phases
        self.phase_1_end = int(0.33 * self.total_samples)  # 0-60s: Healthy
        self.phase_2_end = int(0.67 * self.total_samples)  # 60-120s: Degrading
        # phase_3: 120-180s: Critical
        
    def get_degradation_factor(self):
        """Calculate current degradation factor (0=healthy, 1=critical)"""
        progress = self.current_sample / self.total_samples
        
        if progress <= 0.33:  # Phase 1: Healthy (0-33%)
            return progress * 0.1  # Very slow degradation
        elif progress <= 0.67:  # Phase 2: Degrading (33-67%)
            return 0.1 + (progress - 0.33) * 1.5  # Moderate degradation
        else:  # Phase 3: Critical (67-100%)
            return 0.6 + (progress - 0.67) * 1.2  # Rapid degradation
    
    def simulate_accelerometer(self):
        """
        Simulate ADXL335 accelerometer data with degradation
        Returns: (x_g, y_g, z_g) in g-forces
        """
        degradation = self.get_degradation_factor()
        
        # Base values (machine at rest, Z-axis shows gravity)
        base_x = 0.0
        base_y = 0.0
        base_z = 1.0  # Gravity
        
        # Vibration amplitude increases with degradation
        vibration_amplitude = 0.05 + degradation * 0.4  # 0.05g to 0.45g
        
        # Add some machine operation frequencies
        time_factor = self.current_sample / self.sampling_rate
        
        # Primary machine frequency (gets more chaotic with degradation)
        primary_freq = 2.0 + degradation * 3.0  # 2Hz to 5Hz
        primary_vibration = vibration_amplitude * math.sin(2 * math.pi * primary_freq * time_factor)
        
        # Secondary harmonics (bearing issues)
        if degradation > 0.3:
            harmonic_freq = primary_freq * 2.5
            harmonic_amplitude = degradation * 0.2
            harmonic_vibration = harmonic_amplitude * math.sin(2 * math.pi * harmonic_freq * time_factor)
        else:
            harmonic_vibration = 0
        
        # Random noise (increases with degradation)
        noise_level = 0.02 + degradation * 0.1
        noise_x = random.gauss(0, noise_level)
        noise_y = random.gauss(0, noise_level)
        noise_z = random.gauss(0, noise_level)
        
        # Occasional fault events (more frequent as degradation increases)
        fault_probability = degradation * 0.05  # Up to 5% chance per sample
        fault_spike = 0
        if random.random() < fault_probability:
            fault_spike = random.uniform(0.2, 0.8) * degradation
        
        # Combine all effects
        x_g = base_x + primary_vibration + harmonic_vibration + noise_x + fault_spike
        y_g = base_y + primary_vibration * 0.7 + harmonic_vibration * 0.8 + noise_y + fault_spike * 0.6
        z_g = base_z + primary_vibration * 0.3 + harmonic_vibration * 0.4 + noise_z + fault_spike * 0.3
        
        return x_g, y_g, z_g
    
    def simulate_vibration_sensor(self):
        """
        Simulate vibration sensor voltage with degradation
        Returns: (voltage, level_description)
        """
        degradation = self.get_degradation_factor()
        
        # Base voltage levels
        base_voltage = 0.2  # Quiet baseline
        
        # Vibration increases with degradation
        vibration_voltage = degradation * 2.0  # 0V to 2.0V additional
        
        # Add machine operation patterns
        time_factor = self.current_sample / self.sampling_rate
        
        # Main vibration frequency
        main_freq = 1.5 + degradation * 2.5  # 1.5Hz to 4Hz
        main_vibration = vibration_voltage * 0.5 * (1 + math.sin(2 * math.pi * main_freq * time_factor))
        
        # High frequency content (bearing/gear mesh issues)
        if degradation > 0.4:
            hf_freq = main_freq * 10
            hf_amplitude = degradation * 0.3
            hf_vibration = hf_amplitude * abs(math.sin(2 * math.pi * hf_freq * time_factor))
        else:
            hf_vibration = 0
        
        # Random noise
        noise = random.gauss(0, 0.05 + degradation * 0.1)
        
        # Occasional shock events
        shock_probability = degradation * 0.03
        shock_spike = 0
        if random.random() < shock_probability:
            shock_spike = random.uniform(0.5, 1.5) * degradation
        
        # Total voltage
        total_voltage = base_voltage + main_vibration + hf_vibration + noise + shock_spike
        
        # Clamp to sensor range (0-3.3V)
        voltage = max(0, min(3.3, total_voltage))
        
        # Classify vibration level
        if voltage < 0.5:
            level = "Low/No Vibration"
        elif voltage < 1.2:
            level = "Moderate Vibration"
        else:
            level = "High Vibration"
            
        return voltage, level
    
    def get_current_phase_info(self):
        """Get information about current degradation phase"""
        progress = self.current_sample / self.total_samples
        degradation = self.get_degradation_factor()
        
        if progress <= 0.33:
            phase = "Healthy Operation"
        elif progress <= 0.67:
            phase = "Gradual Degradation"
        else:
            phase = "Critical Condition"
            
        return {
            "phase": phase,
            "progress_percent": progress * 100,
            "degradation_factor": degradation,
            "time_elapsed": self.current_sample / self.sampling_rate,
            "remaining_time": (self.total_samples - self.current_sample) / self.sampling_rate
        }
    
    def get_next_sample(self):
        """
        Get the next sensor sample in the sequence
        Returns: sensor_data dictionary or None if simulation complete
        """
        if self.current_sample >= self.total_samples:
            return None
            
        # Generate sensor data
        x_g, y_g, z_g = self.simulate_accelerometer()
        vib_voltage, vib_level = self.simulate_vibration_sensor()
        
        # Create data packet
        sensor_data = {
            "timestamp": time.time(),
            "sample_number": self.current_sample + 1,
            "accelerometer": {
                "x": round(x_g, 3),
                "y": round(y_g, 3),
                "z": round(z_g, 3)
            },
            "vibration": {
                "voltage": round(vib_voltage, 3),
                "level": vib_level
            },
            "simulation_info": self.get_current_phase_info()
        }
        
        self.current_sample += 1
        return sensor_data
    
    def reset_simulation(self):
        """Reset simulation to beginning"""
        self.current_sample = 0
    
    def is_complete(self):
        """Check if simulation is complete"""
        return self.current_sample >= self.total_samples

# Test function
def test_simulation():
    """Test the simulation and show sample output"""
    print("=== RUL Sensor Simulation Test ===")
    
    # Create simulator (10 second test)
    sim = RULSensorSimulator(duration=10, sampling_rate=1.0)
    
    print(f"Simulating {sim.total_samples} samples over {sim.duration} seconds")
    print("Sample | Time | Phase           | Accel(X,Y,Z)      | Vib(V,Level)")
    print("-" * 75)
    
    while not sim.is_complete():
        data = sim.get_next_sample()
        if data:
            info = data["simulation_info"]
            accel = data["accelerometer"]
            vib = data["vibration"]
            
            print(f"{data['sample_number']:4d}   | {info['time_elapsed']:4.0f}s | {info['phase']:15s} | "
                  f"({accel['x']:+.2f},{accel['y']:+.2f},{accel['z']:+.2f}) | "
                  f"{vib['voltage']:.2f}V,{vib['level']}")

if __name__ == "__main__":
    test_simulation()
