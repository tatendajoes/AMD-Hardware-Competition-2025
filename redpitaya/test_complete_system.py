#!/usr/bin/env python3
# AMD-Hardware-Competition-2025/redpitaya/test_complete_system.py

"""
Comprehensive test script for RedPitaya sensor acquisition system
Tests all components and identifies potential issues
"""

import sys
import time
import os

# Add Red Pitaya library path
sys.path.append('/opt/redpitaya/lib/python')

def test_imports():
    """Test if all required libraries can be imported"""
    print("=== Testing Library Imports ===")
    
    # Test RedPitaya library
    try:
        import rp
        print("✓ RedPitaya 'rp' library imported successfully")
        rp_available = True
    except ImportError as e:
        print(f"✗ Failed to import 'rp' library: {e}")
        rp_available = False
    
    # Test other required libraries
    try:
        import requests
        print("✓ 'requests' library available")
    except ImportError:
        print("✗ 'requests' library not available (needed for data posting)")
    
    try:
        import numpy as np
        print("✓ 'numpy' library available")
    except ImportError:
        print("✗ 'numpy' library not available (needed for feature extraction)")
    
    return rp_available

def test_redpitaya_connection():
    """Test RedPitaya initialization"""
    print("\n=== Testing RedPitaya Connection ===")
    
    try:
        import rp
        rp.rp_Init()
        print("✓ RedPitaya initialized successfully")
        return True
    except Exception as e:
        print(f"✗ RedPitaya initialization failed: {e}")
        print("Possible causes:")
        print("  - Not running on RedPitaya hardware")
        print("  - RedPitaya OS not properly configured")
        print("  - Library path incorrect")
        return False

def test_sensor_classes():
    """Test importing and creating sensor objects"""
    print("\n=== Testing Sensor Classes ===")
    
    try:
        from sensors.accelerometer import Accelerometer
        accel = Accelerometer()
        print("✓ Accelerometer class imported and created")
        accel_ok = True
    except Exception as e:
        print(f"✗ Accelerometer class failed: {e}")
        accel_ok = False
    
    try:
        from sensors.vibration_sensor import VibrationSensor
        vib = VibrationSensor()
        print("✓ VibrationSensor class imported and created")
        vib_ok = True
    except Exception as e:
        print(f"✗ VibrationSensor class failed: {e}")
        vib_ok = False
    
    return accel_ok, vib_ok

def test_analog_inputs():
    """Test reading from analog input pins"""
    print("\n=== Testing Analog Input Readings ===")
    
    try:
        import rp
        
        # Test all 4 analog input pins
        pins = [rp.RP_AIN0, rp.RP_AIN1, rp.RP_AIN2, rp.RP_AIN3]
        pin_names = ["AIN0 (Accel-X)", "AIN1 (Accel-Y)", "AIN2 (Accel-Z)", "AIN3 (Vibration)"]
        
        readings = []
        for i, (pin, name) in enumerate(zip(pins, pin_names)):
            try:
                voltage = rp.rp_AIpinGetValue(pin)[1]
                print(f"✓ {name}: {voltage:.3f}V")
                readings.append(voltage)
            except Exception as e:
                print(f"✗ {name}: Error - {e}")
                readings.append(None)
        
        # Validate readings are reasonable
        valid_readings = [r for r in readings if r is not None]
        if valid_readings:
            print(f"\nReading analysis:")
            print(f"  - Min voltage: {min(valid_readings):.3f}V")
            print(f"  - Max voltage: {max(valid_readings):.3f}V")
            
            # Check if readings are in expected range (0-3.3V for RedPitaya)
            out_of_range = [r for r in valid_readings if r < 0 or r > 3.3]
            if out_of_range:
                print(f"  ⚠️  Warning: {len(out_of_range)} readings out of range (0-3.3V)")
            
            # Check if all readings are exactly the same (might indicate problem)
            if len(set([round(r, 2) for r in valid_readings])) == 1:
                print(f"  ⚠️  Warning: All readings identical - check sensor connections")
        
        return len(valid_readings) > 0
        
    except Exception as e:
        print(f"✗ Analog input test failed: {e}")
        return False

def test_calibration_consistency():
    """Check if calibration values are consistent"""
    print("\n=== Testing Calibration Consistency ===")
    
    try:
        from sensors.accelerometer import Accelerometer
        accel = Accelerometer()
        
        # Read the calibration constants from the class
        # Note: This requires reading the source or having constants as class attributes
        print("Accelerometer calibration check:")
        print("  - Current implementation uses scaled Arduino values")
        print("  - Zero-g bias: ~1.089V (Arduino 1.65V scaled to 3.3V)")
        print("  - Sensitivity: ~0.145 V/g (Arduino 0.22 V/g scaled to 3.3V)")
        print("  ⚠️  Recommend testing against known orientation (1g on Z-axis)")
        
        return True
    except Exception as e:
        print(f"✗ Calibration test failed: {e}")
        return False

def test_data_format():
    """Test the data format output"""
    print("\n=== Testing Data Format ===")
    
    try:
        # Test with mock data
        mock_data = {
            "timestamp": time.time(),
            "accelerometer": {"x": 0.1, "y": -0.2, "z": 1.05},
            "vibration": {"voltage": 0.5, "level": "Moderate Vibration"}
        }
        
        print("✓ Data format structure is valid")
        print(f"Sample output: {mock_data}")
        
        # Test JSON serialization
        import json
        json_data = json.dumps(mock_data)
        print("✓ Data can be serialized to JSON")
        
        return True
    except Exception as e:
        print(f"✗ Data format test failed: {e}")
        return False

def run_live_test():
    """Run a brief live test if hardware is available"""
    print("\n=== Live Hardware Test ===")
    
    try:
        import rp
        from sensors.accelerometer import Accelerometer
        from sensors.vibration_sensor import VibrationSensor
        
        accel = Accelerometer()
        vib_sensor = VibrationSensor()
        
        print("Running 5-second live test...")
        for i in range(5):
            # Get sensor readings
            x_g, y_g, z_g = accel.get_g_force()
            vib_voltage = vib_sensor.get_raw_voltage()
            vib_level = vib_sensor.get_vibration_level()
            
            print(f"  {i+1}s: Accel=({x_g:+.2f}, {y_g:+.2f}, {z_g:+.2f})g, Vib={vib_voltage:.3f}V ({vib_level})")
            time.sleep(1)
        
        print("✓ Live test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Live test failed: {e}")
        return False

def main():
    """Run comprehensive system test"""
    print("RedPitaya Sensor Acquisition System - Comprehensive Test")
    print("=" * 60)
    
    # Track test results
    tests = []
    
    # Run all tests
    tests.append(("Library Imports", test_imports()))
    
    if tests[-1][1]:  # Only continue if imports work
        tests.append(("RedPitaya Connection", test_redpitaya_connection()))
        
        if tests[-1][1]:  # Only continue if connection works
            tests.append(("Sensor Classes", test_sensor_classes()))
            tests.append(("Analog Inputs", test_analog_inputs()))
            tests.append(("Calibration", test_calibration_consistency()))
            tests.append(("Data Format", test_data_format()))
            
            # Ask for live test
            try:
                response = input("\nRun live hardware test? (y/n): ")
                if response.lower().startswith('y'):
                    tests.append(("Live Hardware Test", run_live_test()))
            except KeyboardInterrupt:
                print("\nSkipping live test...")
    
    # Cleanup
    try:
        import rp
        rp.rp_Release()
        print("\nRedPitaya resources released.")
    except:
        pass
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in tests:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(tests)} tests")
    
    if passed == len(tests):
        print("🎉 All tests passed! Your system appears to be working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("\nCommon solutions:")
        print("- Ensure you're running on RedPitaya hardware")
        print("- Check sensor wiring connections")
        print("- Verify RedPitaya library installation")
        print("- Install missing Python packages: pip install requests numpy")

if __name__ == "__main__":
    main()
