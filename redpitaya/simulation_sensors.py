# AMD-Hardware-Competition-2025/redpitaya/simulation_sensors.py

"""
Simulated sensor classes that match the interface of real sensors
Used for data injection into the main acquisition system
"""

from sensor_simulation import RULSensorSimulator

class SimulatedAccelerometer:
    """Simulated accelerometer that matches real Accelerometer interface"""
    
    def __init__(self, simulator):
        """
        Initialize with a reference to the main simulator
        :param simulator: RULSensorSimulator instance
        """
        self.simulator = simulator
        self._last_data = None
    
    def get_g_force(self):
        """
        Get simulated g-force data
        Returns: (x_g, y_g, z_g)
        """
        if self._last_data:
            accel = self._last_data["accelerometer"]
            return accel["x"], accel["y"], accel["z"]
        else:
            return 0.0, 0.0, 1.0  # Default gravity reading
    
    def get_raw_voltage(self):
        """
        Get simulated raw voltage (for compatibility)
        Returns: (x_volt, y_volt, z_volt)
        """
        x_g, y_g, z_g = self.get_g_force()
        
        # Convert g-force back to voltage using same calibration as real sensor
        ZERO_G_BIAS = 1.089  # From accelerometer.py
        SENSITIVITY = 0.145   # From accelerometer.py
        
        x_volt = (x_g * SENSITIVITY) + ZERO_G_BIAS
        y_volt = (y_g * SENSITIVITY) + ZERO_G_BIAS
        z_volt = (z_g * SENSITIVITY) + ZERO_G_BIAS
        
        return x_volt, y_volt, z_volt
    
    def update_data(self, sensor_data):
        """Update with new simulation data"""
        self._last_data = sensor_data

class SimulatedVibrationSensor:
    """Simulated vibration sensor that matches real VibrationSensor interface"""
    
    def __init__(self, simulator):
        """
        Initialize with a reference to the main simulator
        :param simulator: RULSensorSimulator instance
        """
        self.simulator = simulator
        self._last_data = None
    
    def get_raw_voltage(self):
        """
        Get simulated vibration voltage
        Returns: voltage
        """
        if self._last_data:
            return self._last_data["vibration"]["voltage"]
        else:
            return 0.2  # Default quiet voltage
    
    def get_vibration_level(self):
        """
        Get simulated vibration level
        Returns: level description string
        """
        if self._last_data:
            return self._last_data["vibration"]["level"]
        else:
            return "Low/No Vibration"
    
    def update_data(self, sensor_data):
        """Update with new simulation data"""
        self._last_data = sensor_data
