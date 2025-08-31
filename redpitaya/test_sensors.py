# AMD-Hardware-Competition-2025/redpitaya/test_sensors.py

import sys
import time
# Add Red Pitaya library path
sys.path.append('/opt/redpitaya/lib/python')

try:
    import redpitaya_scpi as scpi
except ImportError:
    # Try alternative import
    try:
        import rp_scpi as scpi
    except ImportError:
        print("Error: Could not import Red Pitaya SCPI library")
        print("Available Python paths:")
        for path in sys.path:
            print(f"  {path}")
        sys.exit(1)

def test_connection():
    """Test if we can connect to the Red Pitaya"""
    try:
        print("Connecting to Red Pitaya...")
        rp_s = scpi.scpi('rp-f0d25d.local')
        print("✓ Connection successful!")
        return rp_s
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return None

def test_raw_analog_inputs(rp_s):
    """Test reading raw analog voltages from all 4 pins"""
    print("\n--- Testing Raw Analog Inputs ---")
    try:
        for pin in range(4):  # AIN0, AIN1, AIN2, AIN3
            voltage = float(rp_s.tx_txt(f'ANALOG:PIN? AIN{pin}'))
            print(f"AIN{pin}: {voltage:.3f}V")
        return True
    except Exception as e:
        print(f"✗ Error reading analog inputs: {e}")
        return False

def test_accelerometer(rp_s):
    """Test the accelerometer readings"""
    print("\n--- Testing Accelerometer (ADXL335) ---")
    try:
        # Read X, Y, Z axes (AIN0, AIN1, AIN2)
        x_volt = float(rp_s.tx_txt('ANALOG:PIN? AIN0'))
        y_volt = float(rp_s.tx_txt('ANALOG:PIN? AIN1'))
        z_volt = float(rp_s.tx_txt('ANALOG:PIN? AIN2'))
        
        print(f"X-axis (AIN0): {x_volt:.3f}V")
        print(f"Y-axis (AIN1): {y_volt:.3f}V")
        print(f"Z-axis (AIN2): {z_volt:.3f}V")
        
        # Convert to G-forces (basic conversion)
        VCC = 3.3
        ZERO_G_BIAS = VCC / 2  # 1.65V for 0g
        SENSITIVITY = 0.3      # 300mV/g
        
        x_g = (x_volt - ZERO_G_BIAS) / SENSITIVITY
        y_g = (y_volt - ZERO_G_BIAS) / SENSITIVITY
        z_g = (z_volt - ZERO_G_BIAS) / SENSITIVITY
        
        print(f"Converted: X={x_g:.2f}g, Y={y_g:.2f}g, Z={z_g:.2f}g")
        return True
    except Exception as e:
        print(f"✗ Error reading accelerometer: {e}")
        return False

def test_vibration_sensor(rp_s):
    """Test the vibration sensor readings"""
    print("\n--- Testing Vibration Sensor ---")
    try:
        # Read vibration sensor (AIN3)
        vib_volt = float(rp_s.tx_txt('ANALOG:PIN? AIN3'))
        print(f"Vibration sensor (AIN3): {vib_volt:.3f}V")
        
        # Simple vibration level classification
        if vib_volt > 1.0:
            level = "High Vibration"
        elif vib_volt > 0.1:
            level = "Moderate Vibration"
        else:
            level = "Low/No Vibration"
        
        print(f"Vibration level: {level}")
        return True
    except Exception as e:
        print(f"✗ Error reading vibration sensor: {e}")
        return False

def continuous_monitoring(rp_s):
    """Continuously monitor all sensors"""
    print("\n--- Continuous Monitoring (Press Ctrl+C to stop) ---")
    try:
        while True:
            # Read all sensors
            x_volt = float(rp_s.tx_txt('ANALOG:PIN? AIN0'))
            y_volt = float(rp_s.tx_txt('ANALOG:PIN? AIN1'))
            z_volt = float(rp_s.tx_txt('ANALOG:PIN? AIN2'))
            vib_volt = float(rp_s.tx_txt('ANALOG:PIN? AIN3'))
            
            # Convert accelerometer to g-forces
            VCC = 3.3
            ZERO_G_BIAS = VCC / 2
            SENSITIVITY = 0.3
            
            x_g = (x_volt - ZERO_G_BIAS) / SENSITIVITY
            y_g = (y_volt - ZERO_G_BIAS) / SENSITIVITY
            z_g = (z_volt - ZERO_G_BIAS) / SENSITIVITY
            
            # Display results
            print(f"Accel: X={x_g:+.2f}g Y={y_g:+.2f}g Z={z_g:+.2f}g | Vib: {vib_volt:.3f}V")
            
            time.sleep(0.5)  # Update every 500ms
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
    except Exception as e:
        print(f"\nError during monitoring: {e}")

def main():
    print("=== Red Pitaya Sensor Test ===")
    
    # Test connection
    rp_s = test_connection()
    if not rp_s:
        sys.exit(1)
    
    try:
        # Run all tests
        test_raw_analog_inputs(rp_s)
        test_accelerometer(rp_s)
        test_vibration_sensor(rp_s)
        
        # Ask user if they want continuous monitoring
        response = input("\nDo you want to start continuous monitoring? (y/n): ")
        if response.lower().startswith('y'):
            continuous_monitoring(rp_s)
            
    finally:
        rp_s.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()
