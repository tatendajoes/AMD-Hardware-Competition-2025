# Web Server for AMD Hardware Competition

This directory contains the Flask web server that:
1. Receives sensor data from the Red Pitaya via a POST request.
2. (Will) load a pre-trained machine learning model.
3. (Will) use the model to make predictions based on the incoming sensor data.

## How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. Run the server: `python app.py`

The server will start on `0.0.0.0:5000`, making it accessible to other devices on the same network.
