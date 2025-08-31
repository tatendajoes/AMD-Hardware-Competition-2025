# AMD-Hardware-Competition-2025/redpitaya/data_posting.py

import requests
import json
import time
import config

def post_data(sensor_data):
    """
    Posts sensor data to the web server.
    
    :param sensor_data: A dictionary containing the sensor readings.
    """
    url = f"http://{config.WEBSERVER_IP}:{config.WEBSERVER_PORT}/data"
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, data=json.dumps(sensor_data), headers=headers, timeout=5)
        
        if response.status_code == 200:
            print(f"Successfully posted data. Server response: {response.json()}")
        else:
            print(f"Failed to post data. Status code: {response.status_code}, Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error posting data: {e}")

if __name__ == '__main__':
    # Example usage:
    # This script can be run to test posting mock data to the server.
    print("Testing data posting...")
    
    # Mock sensor data
    mock_data = {
        "timestamp": time.time(),
        "accelerometer": {
            "x": 0.1,
            "y": -0.2,
            "z": 1.05
        },
        "vibration": {
            "voltage": 0.5,
            "level": "Moderate Vibration"
        }
    }
    
    post_data(mock_data)
