# AMD-Hardware-Competition-2025/redpitaya/config.py

# Red Pitaya Configuration
RED_PITAYA_IP = 'rp-f0d25d.local'  # IMPORTANT: Change this to your Red Pitaya's actual IP address

# Data Acquisition Configuration
SAMPLING_INTERVAL = 1  # Time in seconds between each data sample

# Web Server Configuration
WEBSERVER_IP = '192.168.1.50'  # IMPORTANT: Change this to the IP address of the computer running the webserver
WEBSERVER_PORT = 5000

# Sensor Pin Configuration (matches the hardware setup)
# ADXL335 Accelerometer
ACCEL_X_PIN = 0  # Connected to AIN0
ACCEL_Y_PIN = 1  # Connected to AIN1
ACCEL_Z_PIN = 2  # Connected to AIN2

# Vibration Sensor
VIBRATION_PIN = 3 # Connected to AIN3
