# AMD-Hardware-Competition-2025/redpitaya/data_acquisition.py

import sys
import time
import argparse

# Add Red Pitaya library path
sys.path.append('/opt/redpitaya/lib/python')

from sensors.accelerometer import Accelerometer
from sensors.vibration_sensor import VibrationSensor
from simulation_sensors import SimulatedAccelerometer, SimulatedVibrationSensor
from sensor_simulation import RULSensorSimulator
import config

def setup_real_sensors():
    """Initialize real hardware sensors"""
    try:
        import rp
        rp.rp_Init()
        print("Red Pitaya initialized successfully!")
        
        accel = Accelerometer()
        vibe_sensor = VibrationSensor()
        
        return accel, vibe_sensor, rp
    except Exception as e:
        print(f"Failed to initialize real sensors: {e}")
        return None, None, None

def setup_simulation_sensors():
    """Initialize simulated sensors"""
    print("Initializing sensor simulation...")
    
    # Create simulator for 3 minutes
    simulator = RULSensorSimulator(duration=180, sampling_rate=1/config.SAMPLING_INTERVAL)
    
    # Create simulated sensor objects
    accel = SimulatedAccelerometer(simulator)
    vibe_sensor = SimulatedVibrationSensor(simulator)
    
    print("Sensor simulation initialized successfully!")
    print(f"Simulation will run for {simulator.duration} seconds ({simulator.total_samples} samples)")
    
    return accel, vibe_sensor, simulator

def main():
    """
    Main function to acquire data from sensors (real or simulated).
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='RedPitaya Sensor Data Acquisition')
    parser.add_argument('--mode', choices=['sensors', 'simulation'], default='sensors',
                       help='Data source: "sensors" for real hardware, "simulation" for simulated data')
    parser.add_argument('--post-data', action='store_true',
                       help='Enable posting data to web server')
    parser.add_argument('--server-ip', default=config.WEBSERVER_IP,
                       help=f'Web server IP address (default: {config.WEBSERVER_IP})')
    parser.add_argument('--server-port', type=int, default=config.WEBSERVER_PORT,
                       help=f'Web server port (default: {config.WEBSERVER_PORT})')
    args = parser.parse_args()
    
    print(f"=== RedPitaya Data Acquisition ===")
    print(f"Mode: {args.mode}")
    print(f"Sampling interval: {config.SAMPLING_INTERVAL} seconds")
    if args.post_data:
        print(f"Posting data to: http://{args.server_ip}:{args.server_port}/data")
    else:
        print("Data posting: DISABLED (use --post-data to enable)")
    print("=" * 40)
    
    # Update config with command line values
    config.WEBSERVER_IP = args.server_ip
    config.WEBSERVER_PORT = args.server_port
    
    # Initialize based on mode
    if args.mode == 'simulation':
        accel, vibe_sensor, simulator = setup_simulation_sensors()
        rp_handle = None
        use_simulation = True
    else:
        accel, vibe_sensor, rp_handle = setup_real_sensors()
        simulator = None
        use_simulation = False
        
        if accel is None:
            print("Failed to initialize real sensors. Exiting.")
            return
    
    # Import data posting if enabled
    if args.post_data:
        try:
            from data_posting import post_data
            print("Data posting module loaded successfully.")
        except ImportError as e:
            print(f"Error: Could not import data posting module: {e}")
            print("Data will be displayed only.")
            args.post_data = False
    
    try:
        print("Starting data acquisition...")
        sample_count = 0
        
        while True:
            start_time = time.time()
            
            if use_simulation:
                # Get next simulation sample
                sim_data = simulator.get_next_sample()
                
                if sim_data is None:
                    print("Simulation completed!")
                    break
                
                # Update simulated sensors with new data
                accel.update_data(sim_data)
                vibe_sensor.update_data(sim_data)
                
                # Extract sensor readings (same interface as real sensors)
                x_g, y_g, z_g = accel.get_g_force()
                vibration_voltage = vibe_sensor.get_raw_voltage()
                vibration_level = vibe_sensor.get_vibration_level()
                
                # Add simulation info to output
                simulation_info = sim_data["simulation_info"]
                
            else:
                # Get real sensor data
                x_g, y_g, z_g = accel.get_g_force()
                vibration_voltage = vibe_sensor.get_raw_voltage()
                vibration_level = vibe_sensor.get_vibration_level()
                simulation_info = None

            # Prepare data payload (IDENTICAL format for both modes)
            sensor_data = {
                "timestamp": time.time(),
                "accelerometer": {
                    "x": round(x_g, 3),
                    "y": round(y_g, 3),
                    "z": round(z_g, 3)
                },
                "vibration": {
                    "voltage": round(vibration_voltage, 3),
                    "level": vibration_level
                }
            }
            
            # NOTE: This is the EXACT same format as the original data_acquisition.py
            # Whether data comes from real sensors or simulation, the posted data is identical

            # Display data (same format for both modes)
            status_msg = f"[{sample_count+1:3d}] Accel: ({x_g:+.2f},{y_g:+.2f},{z_g:+.2f})g | " \
                        f"Vib: {vibration_voltage:.2f}V ({vibration_level})"
            
            # Add simulation phase info to display only (not to posted data)
            if use_simulation and simulation_info:
                phase = simulation_info["phase"]
                progress = simulation_info["progress_percent"]
                status_msg += f" | {phase} ({progress:4.1f}%)"
            
            # Post data if enabled
            if args.post_data:
                try:
                    post_data(sensor_data)
                    print(f"{status_msg} | ✓ Posted")
                except Exception as e:
                    print(f"{status_msg} | ✗ Post failed: {e}")
            else:
                print(status_msg)
            
            sample_count += 1
            
            # Calculate sleep time to maintain sampling rate
            elapsed = time.time() - start_time
            sleep_time = max(0, config.SAMPLING_INTERVAL - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\nData acquisition stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Cleanup
        if rp_handle:
            try:
                rp_handle.rp_Release()
                print("Red Pitaya resources released.")
            except:
                pass

if __name__ == "__main__":
    main()
