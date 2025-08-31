# AMD-Hardware-Competition-2025/redpitaya/data_acquisition.py

import sys
import time
# Add Red Pitaya library path
sys.path.append('/opt/redpitaya/lib/python')
import rp

from sensors.accelerometer import Accelerometer
from sensors.vibration_sensor import VibrationSensor
import config

def main():
    """
    Main function to acquire data from all sensors.
    """
    try:
        # Initialize Red Pitaya
        rp.rp_Init()
        print("Red Pitaya initialized successfully!")
        
        accel = Accelerometer()
        vibe_sensor = VibrationSensor()

        print("Starting data acquisition...")
        while True:
            # Get accelerometer data
            x_g, y_g, z_g = accel.get_g_force()
            
            # Get vibration data
            vibration_voltage = vibe_sensor.get_raw_voltage()
            vibration_level = vibe_sensor.get_vibration_level()

            # Prepare data payload
            sensor_data = {
                "timestamp": time.time(),
                "accelerometer": {
                    "x": x_g,
                    "y": y_g,
                    "z": z_g
                },
                "vibration": {
                    "voltage": vibration_voltage,
                    "level": vibration_level
                }
            }

            print(sensor_data)
            
            # In a real application, you would pass this data to the data_posting module
            # from data_posting import post_data
            # post_data(sensor_data)

            time.sleep(config.SAMPLING_INTERVAL)

    except KeyboardInterrupt:
        print("Data acquisition stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        try:
            rp.rp_Release()
            print("Red Pitaya resources released.")
        except:
            pass

if __name__ == "__main__":
    main()
