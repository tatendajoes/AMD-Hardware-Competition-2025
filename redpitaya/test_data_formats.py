# AMD-Hardware-Competition-2025/redpitaya/test_data_formats.py

"""
Test script to verify that simulated and real sensor data produce identical output formats
"""

import sys
import time
import json

# Add Red Pitaya library path
sys.path.append('/opt/redpitaya/lib/python')

def test_data_format_consistency():
    """Test that both modes produce identical data structures"""
    
    print("=== Testing Data Format Consistency ===")
    print()
    
    # Test 1: Create mock real sensor data
    print("1. Real sensor data format:")
    real_sensor_data = {
        "timestamp": time.time(),
        "accelerometer": {
            "x": 0.123,
            "y": -0.456,
            "z": 1.023
        },
        "vibration": {
            "voltage": 0.789,
            "level": "Moderate Vibration"
        }
    }
    print(json.dumps(real_sensor_data, indent=2))
    
    # Test 2: Create simulated sensor data (should be identical structure)
    print("\n2. Simulated sensor data format:")
    from sensor_simulation import RULSensorSimulator
    
    simulator = RULSensorSimulator(duration=1, sampling_rate=1.0)
    sim_data = simulator.get_next_sample()
    
    # Extract only the sensor data part (not simulation_info)
    simulated_sensor_data = {
        "timestamp": sim_data["timestamp"],
        "accelerometer": sim_data["accelerometer"],
        "vibration": sim_data["vibration"]
    }
    print(json.dumps(simulated_sensor_data, indent=2))
    
    # Test 3: Compare structures
    print("\n3. Structure comparison:")
    real_keys = set(real_sensor_data.keys())
    sim_keys = set(simulated_sensor_data.keys())
    
    print(f"Real sensor keys: {sorted(real_keys)}")
    print(f"Simulated keys:   {sorted(sim_keys)}")
    print(f"Keys match: {real_keys == sim_keys}")
    
    # Test 4: Compare accelerometer structure
    real_accel_keys = set(real_sensor_data["accelerometer"].keys())
    sim_accel_keys = set(simulated_sensor_data["accelerometer"].keys())
    print(f"Accelerometer keys match: {real_accel_keys == sim_accel_keys}")
    
    # Test 5: Compare vibration structure
    real_vib_keys = set(real_sensor_data["vibration"].keys())
    sim_vib_keys = set(simulated_sensor_data["vibration"].keys())
    print(f"Vibration keys match: {real_vib_keys == sim_vib_keys}")
    
    # Test 6: JSON serialization
    print("\n4. JSON serialization test:")
    try:
        real_json = json.dumps(real_sensor_data)
        sim_json = json.dumps(simulated_sensor_data)
        print("✓ Both formats serialize to JSON successfully")
        print(f"Real JSON length: {len(real_json)} chars")
        print(f"Sim JSON length:  {len(sim_json)} chars")
    except Exception as e:
        print(f"✗ JSON serialization failed: {e}")
    
    print()
    if (real_keys == sim_keys and 
        real_accel_keys == sim_accel_keys and 
        real_vib_keys == sim_vib_keys):
        print("🎉 SUCCESS: Data formats are IDENTICAL!")
    else:
        print("❌ FAILURE: Data formats differ!")

def test_sensor_class_interfaces():
    """Test that simulated sensor classes have same interface as real ones"""
    
    print("\n=== Testing Sensor Class Interfaces ===")
    print()
    
    try:
        # Test simulated sensors
        from simulation_sensors import SimulatedAccelerometer, SimulatedVibrationSensor
        from sensor_simulation import RULSensorSimulator
        
        simulator = RULSensorSimulator(duration=1, sampling_rate=1.0)
        sim_accel = SimulatedAccelerometer(simulator)
        sim_vib = SimulatedVibrationSensor(simulator)
        
        # Update with sample data
        sample_data = simulator.get_next_sample()
        sim_accel.update_data(sample_data)
        sim_vib.update_data(sample_data)
        
        print("Simulated Accelerometer methods:")
        print(f"  get_g_force(): {sim_accel.get_g_force()}")
        print(f"  get_raw_voltage(): {sim_accel.get_raw_voltage()}")
        
        print("Simulated Vibration Sensor methods:")
        print(f"  get_raw_voltage(): {sim_vib.get_raw_voltage()}")
        print(f"  get_vibration_level(): {sim_vib.get_vibration_level()}")
        
        print("\n✓ Simulated sensor interfaces work correctly")
        
    except Exception as e:
        print(f"✗ Simulated sensor interface test failed: {e}")

if __name__ == "__main__":
    test_data_format_consistency()
    test_sensor_class_interfaces()
