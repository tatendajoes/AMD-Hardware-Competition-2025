# AMD-Hardware-Competition-2025/redpitaya/sensors/vibration_sensor.py

import sys
import time
# Add Red Pitaya library path
sys.path.append('/opt/redpitaya/lib/python')
import rp

# Vibration sensor is connected to AIN3

class VibrationSensor:
    def __init__(self, signal_pin=3):
        """
        Initializes the Vibration sensor.
        :param signal_pin: Analog in pin for the sensor's signal (0-3).
        """
        self.signal_pin = signal_pin
        
        # Map pin numbers to Red Pitaya constants
        self.pin_map = {
            0: rp.RP_AIN0,
            1: rp.RP_AIN1,
            2: rp.RP_AIN2,
            3: rp.RP_AIN3
        }

    def get_raw_voltage(self):
        """
        Reads the raw voltage from the vibration sensor.
        """
        return rp.rp_AIpinGetValue(self.pin_map[self.signal_pin])[1]

    def get_vibration_level(self):
        """
        Returns the vibration level. For a simple analog sensor, this might just be the raw voltage.
        You can add logic here to detect a "vibration event" if the voltage exceeds a threshold.
        """
        voltage = self.get_raw_voltage()
        # Example: return a simple classification
        if voltage > 1.0: # This threshold is an example, you need to determine it experimentally
            return "High Vibration"
        elif voltage > 0.1:
            return "Moderate Vibration"
        else:
            return "Low/No Vibration"


if __name__ == '__main__':
    # Example usage:
    try:
        # Initialize Red Pitaya
        rp.rp_Init()
        print("Red Pitaya initialized successfully!")
        
        vibe_sensor = VibrationSensor()

        while True:
            level = vibe_sensor.get_vibration_level()
            voltage = vibe_sensor.get_raw_voltage()
            print(f"Vibration Level: {level} (Voltage: {voltage:.3f}V)")
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"Error: {e}")

    finally:
        try:
            rp.rp_Release()
            print("Red Pitaya resources released.")
        except:
            pass
