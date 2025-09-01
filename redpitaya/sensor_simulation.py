# AMD-Hardware-Competition-2025/redpitaya/sensor_simulation.py

import numpy as np
import time
import math
import random

class RULSensorSimulator:
    """
    Sensor data simulator for RUL prediction testing.
    Simulates progressive equipment degradation over 6 months.
    180 samples represent 6 months of operation (1 sample per day).
    """
    
    def __init__(self, duration=180, sampling_rate=1.0):
        """
        Initialize simulator.
        duration: Total simulation samples (180 = 6 months)
        sampling_rate: Collection rate in Hz for real-time mode
        """
        self.duration = duration
        self.sampling_rate = sampling_rate
        self.total_samples = int(duration * sampling_rate)
        self.current_sample = 0
        
        # Equipment degradation phases over 6 months
        self.phase_1_end = int(0.40 * self.total_samples)  # 0-2.4 months: Normal operation
        self.phase_2_end = int(0.70 * self.total_samples)  # 2.4-4.2 months: Early wear
        self.phase_3_end = int(0.90 * self.total_samples)  # 4.2-5.4 months: Degradation
        # Final phase: 5.4-6 months: Critical condition
        
    def get_degradation_factor(self):
        """Calculate degradation factor (0=new, 1=failed)"""
        progress = self.current_sample / self.total_samples
        
        if progress <= 0.40:  # Normal operation (0-2.4 months)
            return progress * 0.05  # Minimal wear: 0% → 2%
        elif progress <= 0.70:  # Early wear (2.4-4.2 months)
            return 0.02 + (progress - 0.40) * 0.60  # Gradual: 2% → 20%
        elif progress <= 0.90:  # Clear degradation (4.2-5.4 months)
            return 0.20 + (progress - 0.70) * 2.0  # Noticeable: 20% → 60%
        else:  # Critical condition (5.4-6 months)
            return 0.60 + (progress - 0.90) * 4.0  # Rapid: 60% → 100%
    
    def simulate_accelerometer(self):
        """
        Generate ADXL335 accelerometer data with equipment degradation.
        Returns: (x_g, y_g, z_g) acceleration values in g-forces
        """
        degradation = self.get_degradation_factor()
        
        # Base acceleration (equipment at rest, gravity on Z-axis)
        base_x = 0.0
        base_y = 0.0
        base_z = 1.0  # 1g gravity
        
        # Vibration increases with wear
        vibration_amplitude = 0.05 + degradation * 0.4  # 0.05g to 0.45g
        
        # Machine operating frequencies
        time_factor = self.current_sample / self.sampling_rate
        
        # Main vibration frequency (becomes irregular with wear)
        primary_freq = 2.0 + degradation * 3.0  # 2Hz to 5Hz
        primary_vibration = vibration_amplitude * math.sin(2 * math.pi * primary_freq * time_factor)
        
        # Harmonic content (bearing/gear issues in worn equipment)
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
        Generate vibration sensor voltage with equipment degradation.
        Returns: (voltage, level_description)
        """
        degradation = self.get_degradation_factor()
        
        # Base voltage levels for 6-month equipment lifecycle
        base_voltage = 0.1  # Quiet baseline for new equipment
        
        # Voltage progression over equipment lifetime
        progress = self.current_sample / self.total_samples
        
        if progress <= 0.40:  # Normal operation
            vibration_voltage = degradation * 0.5  # 0V to 0.25V
        elif progress <= 0.70:  # Early wear
            vibration_voltage = 0.2 + (degradation - 0.02) * 1.5  # 0.2V to 0.7V
        elif progress <= 0.90:  # Clear degradation
            vibration_voltage = 0.7 + (degradation - 0.20) * 2.0  # 0.7V to 1.4V
        else:  # Critical condition
            vibration_voltage = 1.4 + (degradation - 0.60) * 2.25  # 1.4V to 2.3V
        
        # Machine operating patterns
        time_factor = self.current_sample / self.sampling_rate
        
        # Main vibration frequency (increases with wear)
        main_freq = 1.0 + degradation * 1.5  # 1.0Hz to 2.5Hz
        main_vibration = vibration_voltage * 0.3 * (1 + math.sin(2 * math.pi * main_freq * time_factor))
        
        # High frequency noise (bearing/gear issues in worn equipment)
        if degradation > 0.20:  # Appears after 20% degradation
            hf_freq = main_freq * 8
            hf_amplitude = (degradation - 0.20) * 0.25
            hf_vibration = hf_amplitude * abs(math.sin(2 * math.pi * hf_freq * time_factor))
        else:
            hf_vibration = 0
        
        # Background noise
        noise = random.gauss(0, 0.05 + degradation * 0.1)
        
        # Occasional impact events
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
        
        # Updated phase descriptions for 6-month timeline
        if progress <= 0.40:  # 0-2.4 months
            if progress <= 0.10:  # First month
                phase = "New Equipment"
            else:
                phase = "Healthy Operation"
        elif progress <= 0.70:  # 2.4-4.2 months
            phase = "Early Degradation"
        elif progress <= 0.90:  # 4.2-5.4 months
            phase = "Advanced Degradation"
        else:  # 5.4-6 months
            phase = "Critical - Maintenance Required"
            
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
