# AMD-Hardware-Competition-2025/redpitaya/test_sensors_direct.py

import time
import os
import socket

def test_direct_file_access():
    """Try to read analog values directly from file system"""
    print("\n--- Testing Direct File Access ---")
    
    # Common Red Pitaya analog input file paths
    possible_paths = [
        "/sys/bus/iio/devices/iio:device0/in_voltage{}_raw",
        "/sys/bus/iio/devices/iio:device1/in_voltage{}_raw", 
        "/dev/xadc",
        "/proc/redpitaya_analog"
    ]
    
    for path_template in possible_paths:
        print(f"Checking: {path_template}")
        for pin in range(4):
            if "{}" in path_template:
                file_path = path_template.format(pin)
            else:
                file_path = path_template
                
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        value = f.read().strip()
                        print(f"  AIN{pin}: {value} (from {file_path})")
                except Exception as e:
                    print(f"  Error reading {file_path}: {e}")
            else:
                print(f"  {file_path} does not exist")
        
        if not "{}" in path_template:
            break  # Only try once for non-templated paths

def test_scpi_socket():
    """Try to connect to SCPI server directly via socket"""
    print("\n--- Testing Direct SCPI Socket Connection ---")
    
    try:
        # Red Pitaya typically runs SCPI server on port 5000
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect(('localhost', 5000))
        
        print("✓ Connected to SCPI server on port 5000")
        
        # Test reading analog inputs
        for pin in range(4):
            command = f"ANALOG:PIN? AIN{pin}\n"
            sock.send(command.encode())
            response = sock.recv(1024).decode().strip()
            print(f"AIN{pin}: {response}V")
        
        sock.close()
        return True
        
    except Exception as e:
        print(f"✗ Socket connection failed: {e}")
        return False

def test_alternative_imports():
    """Try various ways to import Red Pitaya libraries"""
    print("\n--- Testing Alternative Library Imports ---")
    
    import_attempts = [
        "import redpitaya_scpi as scpi",
        "import rp_scpi as scpi", 
        "import rp",
        "from redpitaya import scpi",
        "import redpitaya",
    ]
    
    for attempt in import_attempts:
        try:
            print(f"Trying: {attempt}")
            exec(attempt)
            print(f"✓ Success with: {attempt}")
            return True
        except ImportError as e:
            print(f"✗ Failed: {e}")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    return False

def check_redpitaya_processes():
    """Check what Red Pitaya processes are running"""
    print("\n--- Checking Red Pitaya Processes ---")
    
    try:
        import subprocess
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        rp_processes = [line for line in lines if 'redpitaya' in line.lower() or 'scpi' in line.lower()]
        
        if rp_processes:
            print("Found Red Pitaya related processes:")
            for process in rp_processes:
                print(f"  {process}")
        else:
            print("No Red Pitaya related processes found")
            
    except Exception as e:
        print(f"Error checking processes: {e}")

def check_available_modules():
    """List available Python modules in Red Pitaya directories"""
    print("\n--- Checking Available Python Modules ---")
    
    directories_to_check = [
        "/opt/redpitaya/lib/python",
        "/home/jupyter/RedPitaya",
        "/usr/local/lib/python3.10/dist-packages"
    ]
    
    for directory in directories_to_check:
        print(f"\nChecking: {directory}")
        if os.path.exists(directory):
            try:
                files = os.listdir(directory)
                python_files = [f for f in files if f.endswith('.py') or f.endswith('.so') or '.' not in f]
                if python_files:
                    print(f"  Found: {python_files}")
                else:
                    print(f"  No Python files found")
            except Exception as e:
                print(f"  Error: {e}")
        else:
            print(f"  Directory does not exist")

def main():
    print("=== Red Pitaya Direct Access Test ===")
    
    # Try different approaches
    check_available_modules()
    check_redpitaya_processes()
    test_alternative_imports()
    test_direct_file_access()
    test_scpi_socket()
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
