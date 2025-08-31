#!/usr/bin/env python3
# AMD-Hardware-Competition-2025/redpitaya/run_acquisition.py

"""
Simple command-line interface for running sensor data acquisition
Supports both real sensors and simulation modes
"""

import sys
import os

def show_usage():
    print("=== RedPitaya Sensor Data Acquisition ===")
    print()
    print("Usage:")
    print("  python3 run_acquisition.py sensors                    # Real sensors, no posting")
    print("  python3 run_acquisition.py simulation                 # Simulated data, no posting")
    print("  python3 run_acquisition.py sensors --post             # Real sensors + post data")
    print("  python3 run_acquisition.py simulation --post          # Simulated data + post data")
    print("  python3 run_acquisition.py                            # Interactive mode")
    print()
    print("Options:")
    print("  --post                    Enable data posting to web server")
    print("  --server-ip IP            Web server IP (default from config)")
    print("  --server-port PORT        Web server port (default from config)")
    print()

def interactive_mode():
    """Ask user which mode to use"""
    print("=== RedPitaya Sensor Data Acquisition ===")
    print()
    print("Select data source:")
    print("  1. Real sensors (hardware)")
    print("  2. Simulated data (3-minute RUL progression)")
    print("  q. Quit")
    print()
    
    while True:
        choice = input("Enter choice (1/2/q): ").strip().lower()
        
        if choice in ['1', 'sensors', 'real']:
            mode = 'sensors'
            break
        elif choice in ['2', 'simulation', 'sim']:
            mode = 'simulation'
            break
        elif choice in ['q', 'quit', 'exit']:
            return None, False
        else:
            print("Invalid choice. Please enter 1, 2, or q.")
    
    print()
    post_choice = input("Enable data posting to web server? (y/n): ").strip().lower()
    post_data = post_choice.startswith('y')
    
    return mode, post_data

def main():
    # Parse arguments
    mode = None
    post_data = False
    extra_args = []
    
    # Check command line arguments
    args = sys.argv[1:]
    
    if len(args) == 0:
        # Interactive mode
        result = interactive_mode()
        if result is None:
            print("Goodbye!")
            return
        mode, post_data = result
    else:
        # Parse command line
        i = 0
        while i < len(args):
            arg = args[i].lower()
            
            if arg in ['sensors', 'real', 'hardware']:
                mode = 'sensors'
            elif arg in ['simulation', 'sim', 'simulate']:
                mode = 'simulation'
            elif arg in ['--post', '--post-data']:
                post_data = True
            elif arg in ['--server-ip'] and i + 1 < len(args):
                extra_args.extend(['--server-ip', args[i + 1]])
                i += 1
            elif arg in ['--server-port'] and i + 1 < len(args):
                extra_args.extend(['--server-port', args[i + 1]])
                i += 1
            elif arg in ['help', '-h', '--help']:
                show_usage()
                return
            else:
                print(f"Error: Unknown argument '{args[i]}'")
                show_usage()
                return
            i += 1
    
    if mode is None:
        print("Error: No mode specified")
        show_usage()
        return
    
    print(f"\nStarting data acquisition:")
    print(f"  Mode: {mode}")
    print(f"  Data posting: {'ENABLED' if post_data else 'DISABLED'}")
    print("Press Ctrl+C to stop.\n")
    
    # Import and run the main acquisition script
    try:
        # Build command line arguments for data_acquisition.py
        cmd_args = ['data_acquisition.py', '--mode', mode]
        if post_data:
            cmd_args.append('--post-data')
        cmd_args.extend(extra_args)
        
        # Modify sys.argv to pass the arguments
        original_argv = sys.argv[:]
        sys.argv = cmd_args
        
        # Import and run
        from data_acquisition import main as run_acquisition
        run_acquisition()
        
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except ImportError as e:
        print(f"Error importing data_acquisition module: {e}")
        print("Make sure you're in the correct directory with all required files.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Restore original argv
        sys.argv = original_argv

if __name__ == "__main__":
    main()
