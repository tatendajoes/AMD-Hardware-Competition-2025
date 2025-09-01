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
    """Initialize hardware sensors"""
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
    """Initialize simulation sensors"""
    print("Initializing sensor simulation...")
    
    # Create simulator for 6-month equipment lifecycle
    simulator = RULSensorSimulator(duration=180, sampling_rate=1/config.SAMPLING_INTERVAL)
    
    # Create simulated sensor objects
    accel = SimulatedAccelerometer(simulator)
    vibe_sensor = SimulatedVibrationSensor(simulator)
    
    print("Sensor simulation initialized successfully!")
    print(f"Simulation represents 6 months of equipment operation ({simulator.total_samples} samples)")
    print("Timeline: Each sample represents 1 day of operation")
    
    return accel, vibe_sensor, simulator

def main():
    """
    Data acquisition from sensors (hardware or simulated).
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
    parser.add_argument('--batch-size', type=int, default=100,
                       help='Number of samples to collect before posting (default: 100)')
    parser.add_argument('--individual-samples', action='store_true',
                       help='Send individual samples instead of batches (original behavior)')
    args = parser.parse_args()
    
    print(f"=== RedPitaya Data Acquisition ===")
    print(f"Mode: {args.mode}")
    print(f"Sampling interval: {config.SAMPLING_INTERVAL} seconds")
    if args.post_data:
        print(f"Posting data to: http://{args.server_ip}:{args.server_port}/data")
        if args.individual_samples:
            print("Data format: Individual samples")
        else:
            print(f"Data format: Batches of {args.batch_size} samples")
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
    
    # Initialize batch collection buffers
    if args.post_data and not args.individual_samples:
        accel_x_batch = []
        accel_y_batch = []
        accel_z_batch = []
        vib_voltage_batch = []
        batch_timestamps = []
        print(f"Batch mode: Collecting {args.batch_size} samples before posting...")
    
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
                    # Post any remaining batch data
                    if args.post_data and not args.individual_samples and len(accel_x_batch) > 0:
                        post_batch_data(accel_x_batch, accel_y_batch, accel_z_batch, 
                                      vib_voltage_batch, batch_timestamps, post_data, args.mode)
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

            # Display data (same format for both modes)
            status_msg = f"[{sample_count+1:3d}] Accel: ({x_g:+.2f},{y_g:+.2f},{z_g:+.2f})g | " \
                        f"Vib: {vibration_voltage:.2f}V ({vibration_level})"
            
            # Add simulation phase info to display only (not to posted data)
            if use_simulation and simulation_info:
                phase = simulation_info["phase"]
                progress = simulation_info["progress_percent"]
                status_msg += f" | {phase} ({progress:4.1f}%)"
            
            # Handle data posting
            if args.post_data:
                if args.individual_samples:
                    # Original behavior: post individual samples
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
                    
                    try:
                        post_data(sensor_data)
                        print(f"{status_msg} | ✓ Posted")
                    except Exception as e:
                        print(f"{status_msg} | ✗ Post failed: {e}")
                else:
                    # Batch mode: collect samples
                    accel_x_batch.append(x_g)
                    accel_y_batch.append(y_g)
                    accel_z_batch.append(z_g)
                    vib_voltage_batch.append(vibration_voltage)
                    batch_timestamps.append(time.time())
                    
                    # Check if batch is ready
                    if len(accel_x_batch) >= args.batch_size:
                        try:
                            post_batch_data(accel_x_batch, accel_y_batch, accel_z_batch, 
                                          vib_voltage_batch, batch_timestamps, post_data, args.mode)
                            print(f"{status_msg} | ✓ Batch posted ({len(accel_x_batch)} samples)")
                            
                            # Clear buffers
                            accel_x_batch.clear()
                            accel_y_batch.clear() 
                            accel_z_batch.clear()
                            vib_voltage_batch.clear()
                            batch_timestamps.clear()
                        except Exception as e:
                            print(f"{status_msg} | ✗ Batch post failed: {e}")
                    else:
                        print(f"{status_msg} | Batch: {len(accel_x_batch)}/{args.batch_size}")
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
        # Post any remaining batch data
        if args.post_data and not args.individual_samples and len(accel_x_batch) > 0:
            try:
                post_batch_data(accel_x_batch, accel_y_batch, accel_z_batch, 
                              vib_voltage_batch, batch_timestamps, post_data, args.mode)
                print(f"Posted final batch ({len(accel_x_batch)} samples)")
            except Exception as e:
                print(f"Failed to post final batch: {e}")
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

def post_batch_data(accel_x, accel_y, accel_z, vib_voltage, timestamps, post_func, mode):
    """Post batch data to web server"""
    batch_data = {
        "mode": mode,
        "batch_info": {
            "sample_count": len(accel_x),
            "start_time": timestamps[0],
            "end_time": timestamps[-1],
            "duration": timestamps[-1] - timestamps[0]
        },
        "accel_data": {
            "x": accel_x,
            "y": accel_y, 
            "z": accel_z
        },
        "vib_data": vib_voltage,
        "timestamps": timestamps
    }
    
    post_func(batch_data)

if __name__ == "__main__":
    main()
