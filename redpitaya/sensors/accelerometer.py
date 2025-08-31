# AMD-Hardware-Competition-2025/redpitaya/sensors/accelerometer.py

import sys
import time
# Add Red Pitaya library path
sys.path.append('/opt/redpitaya/lib/python')
import rp

# ADXL335 is connected to AIN0, AIN1, AIN2
# AIN0: X-axis
# AIN1: Y-axis
# AIN2: Z-axis

class Accelerometer:
    def __init__(self, x_pin=0, y_pin=1, z_pin=2):
        """
        Initializes the Accelerometer sensor.
        :param x_pin: Analog in pin for X-axis (0-3).
        :param y_pin: Analog in pin for Y-axis (0-3).
        :param z_pin: Analog in pin for Z-axis (0-3).
        """
        self.x_pin = x_pin
        self.y_pin = y_pin
        self.z_pin = z_pin
        
        # Map pin numbers to Red Pitaya constants
        self.pin_map = {
            0: rp.RP_AIN0,
            1: rp.RP_AIN1,
            2: rp.RP_AIN2,
            3: rp.RP_AIN3
        }

    def get_raw_voltage(self):
        """
        Reads the raw voltage from the accelerometer axes.
        """
        x_volt = rp.rp_AIpinGetValue(self.pin_map[self.x_pin])[1]
        y_volt = rp.rp_AIpinGetValue(self.pin_map[self.y_pin])[1]
        z_volt = rp.rp_AIpinGetValue(self.pin_map[self.z_pin])[1]
        return x_volt, y_volt, z_volt

    def get_g_force(self):
        """
        Converts raw voltage to G-force.
        This will need calibration based on the sensor's datasheet and your specific setup.
        For the ADXL335, sensitivity is typically 300mV/g.
        The zero-g bias is typically VCC/2.
        """
        # Calibration constants - CORRECTED based on Arduino testing
        VCC = 3.3 
        # Scale Arduino calibration values (5V) to Red Pitaya (3.3V)
        ZERO_G_BIAS = 1.65 * (3.3 / 5.0)  # = 1.089V (Arduino: 1.65V @ 5V)
        SENSITIVITY = 0.22 * (3.3 / 5.0)   # = 0.145 V/g (Arduino: 0.22 V/g @ 5V)

        x_volt, y_volt, z_volt = self.get_raw_voltage()

        x_g = (x_volt - ZERO_G_BIAS) / SENSITIVITY
        y_g = (y_volt - ZERO_G_BIAS) / SENSITIVITY
        z_g = (z_volt - ZERO_G_BIAS) / SENSITIVITY
        
        return x_g, y_g, z_g

if __name__ == '__main__':
    # Example usage:
    try:
        # Initialize Red Pitaya
        rp.rp_Init()
        print("Red Pitaya initialized successfully!")
        
        accel = Accelerometer()

        while True:
            x, y, z = accel.get_g_force()
            print(f"G-forces: X={x:.2f}g, Y={y:.2f}g, Z={z:.2f}g")
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

