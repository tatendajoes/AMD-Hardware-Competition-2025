# AMD-Hardware-Competition-2025/redpitaya/test_sensors_working.py

import sys
import time
# Add Red Pitaya library path
sys.path.append('/opt/redpitaya/lib/python')

import rp

def test_connection():
    """Test if we can connect to the Red Pitaya"""
    try:
        print("Initializing Red Pitaya...")
        rp.rp_Init()
        print("✓ Red Pitaya initialized successfully!")
        return True
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return False

def test_raw_analog_inputs():
    """Test reading raw analog voltages from all 4 pins"""
    print("\n--- Testing Raw Analog Inputs ---")
    try:
        # Red Pitaya analog input pins
        ain_pins = [rp.RP_AIN0, rp.RP_AIN1, rp.RP_AIN2, rp.RP_AIN3]
        
        for i, pin in enumerate(ain_pins):
            voltage = rp.rp_AIpinGetValue(pin)[1]  # [1] gets the actual value
            print(f"AIN{i}: {voltage:.3f}V")
        return True
    except Exception as e:
        print(f"✗ Error reading analog inputs: {e}")
        return False

def test_accelerometer():
    """Test the accelerometer readings"""
    print("\n--- Testing Accelerometer (ADXL335) ---")
    try:
        # Read X, Y, Z axes (AIN0, AIN1, AIN2)
        x_volt = rp.rp_AIpinGetValue(rp.RP_AIN0)[1]
        y_volt = rp.rp_AIpinGetValue(rp.RP_AIN1)[1]
        z_volt = rp.rp_AIpinGetValue(rp.RP_AIN2)[1]
        
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

def test_vibration_sensor():
    """Test the vibration sensor readings"""
    print("\n--- Testing Vibration Sensor ---")
    try:
        # Read vibration sensor (AIN3)
        vib_volt = rp.rp_AIpinGetValue(rp.RP_AIN3)[1]
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

def continuous_monitoring():
    """Continuously monitor all sensors"""
    print("\n--- Continuous Monitoring (Press Ctrl+C to stop) ---")
    try:
        while True:
            # Read all sensors
            x_volt = rp.rp_AIpinGetValue(rp.RP_AIN0)[1]
            y_volt = rp.rp_AIpinGetValue(rp.RP_AIN1)[1]
            z_volt = rp.rp_AIpinGetValue(rp.RP_AIN2)[1]
            vib_volt = rp.rp_AIpinGetValue(rp.RP_AIN3)[1]
            
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
    print("=== Red Pitaya Sensor Test (Working Version) ===")
    
    # Test connection
    if not test_connection():
        sys.exit(1)
    
    try:
        # Run all tests
        test_raw_analog_inputs()
        test_accelerometer()
        test_vibration_sensor()
        
        # Ask user if they want continuous monitoring
        response = input("\nDo you want to start continuous monitoring? (y/n): ")
        if response.lower().startswith('y'):
            continuous_monitoring()
            
    finally:
        try:
            rp.rp_Release()
            print("Red Pitaya resources released.")
        except:
            pass

if __name__ == "__main__":
    main()
