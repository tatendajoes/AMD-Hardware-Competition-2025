# AMD-Hardware-Competition-2025/webserver/app.py

from flask import Flask, request, jsonify

app = Flask(__name__)

# In a real application, you would load your trained model here.
# from joblib import load
# model = load('model/your_model.pkl')

@app.route('/')
def index():
    return "Web server is running. POST sensor data to /data."

@app.route('/data', methods=['POST'])
def receive_data():
    """
    Endpoint to receive sensor data from the Red Pitaya.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    print("Received data:", data)

    # --- Model Prediction Step ---
    # 1. Preprocess the data to match the model's input format.
    #    (e.g., extract features, scale values)
    #
    # 2. Make a prediction.
    #    prediction = model.predict(preprocessed_data)
    #
    # 3. Do something with the prediction.
    #    (e.g., log it, trigger an alert)
    
    # For now, we just acknowledge receipt and send back the data.
    # Replace this with your actual model's prediction.
    prediction_result = "No model loaded, but data was received."

    response = {
        "status": "success",
        "received_data": data,
        "prediction": prediction_result
    }
    
    return jsonify(response)

if __name__ == '__main__':
    # Runs the server on 0.0.0.0 to be accessible from the network.
    # Make sure your firewall allows connections on this port.
    app.run(host='0.0.0.0', port=5000, debug=True)
