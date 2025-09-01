# AMD-Hardware-Competition-2025/webserver/app.py


import numpy as np
import pandas as pd
import joblib
import time
from flask import Flask, request, jsonify
import traceback

import sys
sys.path.append('..')  # To allow import from parent if needed


app = Flask(__name__)

# --- Model and Feature Extraction Utilities ---
MODEL_PATH = 'smart_rul_predictor.pkl'

def _safe_entropy(x, bins=10):
    from scipy.stats import entropy
    hist, _ = np.histogram(x, bins=bins)
    p = hist.astype(float)
    s = p.sum()
    if s == 0:
        return 0.0
    p = p / s
    return float(entropy(p + 1e-12, base=np.e))

def get_health_status(rul_hours):
    """Map RUL hours to equipment health status"""
    if rul_hours > 24 * 30:
        return "🟢 EXCELLENT (>30 days)"
    elif rul_hours > 24 * 7:
        return "🟡 GOOD (>7 days)"
    elif rul_hours > 24:
        return "🟠 MODERATE (>1 day)"
    elif rul_hours > 12:
        return "🔴 POOR (>12 hours)"
    else:
        return "⚫ CRITICAL (<12 hours)"

def extract_features(sensor_data):
    """
    Extract 8 time-domain features from sensor data.
    Returns: [RMS, Peak, Mean, Std, Kurtosis, Skewness, Crest Factor, Entropy]
    """
    from scipy import stats
    data = np.array(sensor_data)
    
    # Calculate feature values
    mean_val = float(np.mean(data))
    rms_val = float(np.sqrt(np.mean(data**2)))
    peak_val = float(np.max(np.abs(data)))
    std_val = float(np.std(data))
    kurtosis_val = float(stats.kurtosis(data))
    skewness_val = float(stats.skew(data))
    crest_factor = float(peak_val / rms_val) if rms_val != 0 else 0.0
    entropy_val = _safe_entropy(data, bins=10)
    
    # Return features in order expected by ML model
    return [
        rms_val,        # RMS value
        peak_val,       # Peak amplitude
        mean_val,       # Mean value
        std_val,        # Standard deviation
        kurtosis_val,   # Kurtosis
        skewness_val,   # Skewness
        crest_factor,   # Crest factor
        entropy_val     # Entropy
    ]

def create_nasa_compatible_features(accel_features, vib_features):
    time_features = ['mean', 'std', 'skew', 'kurtosis', 'entropy', 'rms',
                     'max', 'p2p', 'crest', 'clearence', 'shape', 'impulse']
    sensors = ['B1_x', 'B1_y', 'B2_x', 'B2_y', 'B3_x', 'B3_y', 'B4_x', 'B4_y']
    feature_names = [f"{s}_{t}" for s in sensors for t in time_features]
    feature_values = []
    for i, sensor in enumerate(sensors):
        source = accel_features if (i % 2 == 0) else vib_features  # x->accel, y->vib
        mapped = [
            source[0],          # mean
            source[3],          # std
            source[5],          # skew
            source[4],          # kurtosis
            source[7],          # entropy
            source[1],          # rms
            source[2],          # max (peak)
            source[2],          # p2p (approx with peak)
            source[6],          # crest
            source[6] * 0.8,    # clearence (approx)
            (source[1] / source[0]) if source[0] != 0 else 1.0,  # shape
            (source[2] / source[0]) if source[0] != 0 else 1.0,  # impulse
        ]
        feature_values.extend(mapped)
    feature_df = pd.DataFrame([feature_values], columns=feature_names)
    return feature_df

class SmartRULPredictor:
    def __init__(self, model, scaler, time_unit_minutes=10):
        self.model = model
        self.scaler = scaler
        self.time_unit_minutes = time_unit_minutes
    def _prepare_X(self, features):
        if isinstance(features, pd.DataFrame):
            X = features.copy()
            if hasattr(self.scaler, "feature_names_in_"):
                expected = list(self.scaler.feature_names_in_)
                missing = [c for c in expected if c not in X.columns]
                if missing:
                    raise ValueError(f"Missing features for scaler: {missing[:8]}{'...' if len(missing)>8 else ''}")
                X = X[expected]
            return X
        X = np.asarray(features, dtype=float)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        elif X.ndim > 2:
            raise ValueError(f"features has ndim={X.ndim}; expected 1D or 2D")
        return X
    def predict_rul_smart(self, features):
        X = self._prepare_X(features)
        scaled = self.scaler.transform(X)
        pred = self.model.predict(scaled)
        rul_units = float(pred[0])
        rul_hours = rul_units * self.time_unit_minutes / 60.0
        
        # Always prefer days for industrial equipment
        if rul_hours >= 24 * 30:    return self._format_months(rul_hours)
        if rul_hours >= 24 * 7:     return self._format_weeks(rul_hours)
        if rul_hours >= 1:          return self._format_days(rul_hours)  # Changed from 24 to 1
        return self._format_hours(rul_hours)  # Only for very short periods < 1 hour
    def _format_months(self, hours):
        months = int(hours // (24 * 30))
        days   = int((hours % (24 * 30)) // 24)
        return {"value": hours,
                "formatted": f"{months} month{'s' if months!=1 else ''}" + ("" if days==0 else f" {days} day{'s' if days!=1 else ''}"),
                "unit": "months", "months": months, "days": days}
    def _format_weeks(self, hours):
        weeks = int(hours // (24 * 7))
        days  = int((hours % (24 * 7)) // 24)
        return {"value": hours,
                "formatted": f"{weeks} week{'s' if weeks!=1 else ''}" + ("" if days==0 else f" {days} day{'s' if days!=1 else ''}"),
                "unit": "weeks", "weeks": weeks, "days": days}
    def _format_days(self, hours):
        days = int(hours // 24)
        rem  = int(hours % 24)
        return {"value": hours,
                "formatted": f"{days} day{'s' if days!=1 else ''}" + ("" if rem==0 else f" {rem} hour{'s' if rem!=1 else ''}"),
                "unit": "days", "days": days, "hours": rem}
    def _format_hours(self, hours):
        h = int(hours)
        m = int(round((hours - h) * 60))
        if m == 60:
            h += 1; m = 0
        return {"value": hours,
                "formatted": f"{h} hour{'s' if h!=1 else ''}" + ("" if m==0 else f" {m} minute{'s' if m!=1 else ''}"),
                "unit": "hours", "hours": h, "minutes": m}

# --- Load model at startup ---
try:
    predictor_obj = joblib.load(MODEL_PATH)
    if hasattr(predictor_obj, 'model') and hasattr(predictor_obj, 'scaler'):
        predictor = predictor_obj
    elif hasattr(predictor_obj, 'scaler'):
        predictor = SmartRULPredictor(predictor_obj, predictor_obj.scaler)
    else:
        raise Exception('Model/scaler not found in loaded object')
except Exception as e:
    print(f"[ERROR] Could not load model: {e}")
    predictor = None

# In a real application, you would load your trained model here.
# from joblib import load
# model = load('model/your_model.pkl')

@app.route('/')
def index():
    return "Web server is running. POST sensor data to /data or visit /dashboard for the dashboard."

@app.route('/dashboard')
def dashboard():
    """Serve the HTML dashboard"""
    try:
        with open('dashboard.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Dashboard not found. Make sure dashboard.html exists in the webserver directory."

# Store latest prediction for dashboard
latest_prediction = {"status": "waiting", "message": "No predictions yet"}

@app.route('/data', methods=['POST'])
def receive_sensor_data():
    """
    Receives real-time sensor data from RedPitaya
    Supports two formats:
    
    1. Individual samples (original):
    {
        "timestamp": 1756684496.025,
        "accelerometer": {"x": 0.123, "y": -0.456, "z": 1.023},
        "vibration": {"voltage": 0.789, "level": "Moderate Vibration"}
    }
    
    2. Batch data (new):
    {
        "mode": "simulation",
        "batch_info": {"sample_count": 100, "start_time": ..., "end_time": ...},
        "accel_data": {"x": [array], "y": [array], "z": [array]},
        "vib_data": [array],
        "timestamps": [array]
    }
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    try:
        data = request.get_json()
        
        # Detect data format
        if 'batch_info' in data:
            # Handle batch data
            return handle_batch_data(data)
        else:
            # Handle individual sample (original format)
            return handle_individual_sample(data)
            
    except Exception as e:
        print(f"[ERROR] Exception in /data: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def handle_individual_sample(sensor_data):
    """Handle individual sensor sample (original behavior)"""
    # Validate required fields
    required_fields = ['timestamp', 'accelerometer', 'vibration']
    for field in required_fields:
        if field not in sensor_data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Validate accelerometer data
    accel = sensor_data['accelerometer']
    if not all(k in accel for k in ['x', 'y', 'z']):
        return jsonify({"error": "Accelerometer data must have x, y, z fields"}), 400
    
    # Validate vibration data  
    vib = sensor_data['vibration']
    if not all(k in vib for k in ['voltage', 'level']):
        return jsonify({"error": "Vibration data must have voltage, level fields"}), 400
    
    # Log the received data
    timestamp = sensor_data['timestamp']
    accel_x, accel_y, accel_z = accel['x'], accel['y'], accel['z']
    vib_voltage, vib_level = vib['voltage'], vib['level']
    
    print(f"[DATA] {timestamp:.2f} | Accel: ({accel_x:+.3f},{accel_y:+.3f},{accel_z:+.3f})g | Vib: {vib_voltage:.3f}V ({vib_level})")
    
    return jsonify({
        "status": "success", 
        "message": "Individual sensor sample received",
        "timestamp": timestamp
    })

def handle_batch_data(batch_data):
    """Handle batch sensor data and trigger RUL prediction with proper feature extraction"""
    # Validate batch structure
    required_fields = ['batch_info', 'accel_data', 'vib_data', 'timestamps']
    for field in required_fields:
        if field not in batch_data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    batch_info = batch_data['batch_info']
    accel_data = batch_data['accel_data']
    vib_data = batch_data['vib_data']
    timestamps = batch_data['timestamps']
    
    sample_count = batch_info['sample_count']
    duration = batch_info['end_time'] - batch_info['start_time']
    mode = batch_data.get('mode', 'unknown')
    
    print(f"[BATCH] Received {sample_count} samples over {duration:.1f}s (mode: {mode})")
    
    # Extract accelerometer arrays
    accel_x = accel_data['x']
    accel_y = accel_data['y'] 
    accel_z = accel_data['z']
    
    # Log sample statistics
    print(f"  Accel X: {min(accel_x):+.3f} to {max(accel_x):+.3f}g (avg: {sum(accel_x)/len(accel_x):+.3f}g)")
    print(f"  Accel Y: {min(accel_y):+.3f} to {max(accel_y):+.3f}g (avg: {sum(accel_y)/len(accel_y):+.3f}g)")  
    print(f"  Accel Z: {min(accel_z):+.3f} to {max(accel_z):+.3f}g (avg: {sum(accel_z)/len(accel_z):+.3f}g)")
    print(f"  Vibration: {min(vib_data):.3f} to {max(vib_data):.3f}V (avg: {sum(vib_data)/len(vib_data):.3f}V)")
    
    # Trigger RUL prediction if model is available and we have enough data
    rul_prediction = None
    feature_info = None
    
    if predictor is not None and sample_count >= 50:  # Minimum samples for reliable prediction
        try:
            print("  Extracting features from sensor data...")
            
            # Extract 8 features from each sensor axis (4 sensors total = 32 features)
            accel_x_features = extract_features(np.array(accel_x))  # 8 features
            accel_y_features = extract_features(np.array(accel_y))  # 8 features  
            accel_z_features = extract_features(np.array(accel_z))  # 8 features
            vib_features = extract_features(np.array(vib_data))     # 8 features
            
            # Log feature extraction results
            feature_names = ["RMS", "Peak", "Mean", "Std", "Kurtosis", "Skewness", "Crest", "Entropy"]
            print(f"    Accel X features: {[f'{name}={val:.3f}' for name, val in zip(feature_names, accel_x_features)]}")
            print(f"    Accel Y features: {[f'{name}={val:.3f}' for name, val in zip(feature_names, accel_y_features)]}")
            print(f"    Accel Z features: {[f'{name}={val:.3f}' for name, val in zip(feature_names, accel_z_features)]}")
            print(f"    Vibration features: {[f'{name}={val:.3f}' for name, val in zip(feature_names, vib_features)]}")
            
            # Combine features for NASA-compatible format
            # For now, use accelerometer magnitude as primary accel signal and vibration as secondary
            accel_magnitude = [np.sqrt(x**2 + y**2 + z**2) for x, y, z in zip(accel_x, accel_y, accel_z)]
            accel_mag_features = extract_features(np.array(accel_magnitude))
            
            # Create feature DataFrame compatible with trained model
            feature_df = create_nasa_compatible_features(accel_mag_features, vib_features)
            
            # Generate RUL prediction
            rul_prediction = predictor.predict_rul_smart(feature_df)
            
            # Enhanced terminal output
            print(f"  🔮 RUL Prediction: {rul_prediction['formatted']} ({rul_prediction['value']:.1f} hours)")
            print(f"  📊 Health Status: {get_health_status(rul_prediction['value'])}")
            print(f"  ⚡ Vibration Level: {np.mean(vib_data):.2f}V (Peak: {np.max(vib_data):.2f}V)")
            print(f"  📈 Acceleration RMS: {accel_mag_features[0]:.3f}g")
            
            # Store feature info for response
            feature_info = {
                "accel_x_features": accel_x_features,
                "accel_y_features": accel_y_features, 
                "accel_z_features": accel_z_features,
                "vibration_features": vib_features,
                "accel_magnitude_features": accel_mag_features,
                "feature_names": feature_names,
                "total_features_extracted": 32  # 4 sensors × 8 features each
            }
            
            # Store latest prediction globally for dashboard
            global latest_prediction
            latest_prediction = {
                "rul_prediction": rul_prediction,
                "feature_extraction": feature_info,
                "sample_count": sample_count,
                "mode": mode,
                "timestamp": time.time(),
                "batch_info": batch_info,
                "status": "success"
            }
            
        except Exception as e:
            print(f"  ❌ RUL Prediction failed: {e}")
            import traceback
            traceback.print_exc()
            rul_prediction = {"error": str(e)}
    elif sample_count < 50:
        print(f"  ⏳ Need more samples for prediction (have {sample_count}, need ≥50)")
    else:
        print(f"  ❌ Model not loaded - cannot generate predictions")
    
    response = {
        "status": "success",
        "message": "Batch data received and processed",
        "batch_info": batch_info,
        "sample_count": sample_count,
        "mode": mode
    }
    
    if rul_prediction:
        response["rul_prediction"] = rul_prediction
    
    if feature_info:
        response["feature_extraction"] = feature_info
    
    return jsonify(response)


# --- API endpoint for prediction ---
@app.route('/predict', methods=['POST'])
def predict():
    """
    Accepts JSON with either:
      - 'accel_data' and 'vib_data' as lists (raw simulated or real sensor data)
      - or 'features' as a flat list of 8 values for accel, 8 for vib (advanced)
    Returns model prediction or error.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json()
    try:
        if predictor is None:
            return jsonify({"error": "Model not loaded on server."}), 500

        # Accept either raw sensor data or pre-extracted features
        if 'accel_data' in data and 'vib_data' in data:
            accel_data = np.array(data['accel_data'])
            vib_data = np.array(data['vib_data'])
            accel_features = extract_features(accel_data)
            vib_features = extract_features(vib_data)
        elif 'features' in data:
            features = data['features']
            if len(features) != 16:
                return jsonify({"error": "'features' must be a list of 16 values (8 accel, 8 vib)."}), 400
            accel_features = features[:8]
            vib_features = features[8:]
        else:
            return jsonify({"error": "Provide either 'accel_data' and 'vib_data', or 'features'."}), 400

        feature_df = create_nasa_compatible_features(accel_features, vib_features)
        prediction = predictor.predict_rul_smart(feature_df)
        return jsonify({"prediction": prediction, "status": "success"})
    except Exception as e:
        print("[ERROR] Exception in /predict:", e)
        traceback.print_exc()
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

# --- Simulate API call for demonstration ---
@app.route('/simulate', methods=['GET'])
def simulate():
    """
    Simulate a prediction using generated sensor data (for testing the API).
    """
    try:
        samples = int(request.args.get('samples', 1000))
        np.random.seed(42)
        accel_data = np.random.normal(0, 1, samples) + 0.1 * np.sin(np.linspace(0, 10, samples))
        vib_data   = np.random.normal(0, 0.5, samples) + 0.05 * np.cos(np.linspace(0, 15, samples))
        accel_features = extract_features(accel_data)
        vib_features = extract_features(vib_data)
        feature_df = create_nasa_compatible_features(accel_features, vib_features)
        if predictor is None:
            return jsonify({"error": "Model not loaded on server."}), 500
        prediction = predictor.predict_rul_smart(feature_df)
        return jsonify({
            "prediction": prediction,
            "accel_features": accel_features,
            "vib_features": vib_features,
            "status": "success"
        })
    except Exception as e:
        print("[ERROR] Exception in /simulate:", e)
        traceback.print_exc()
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route('/latest', methods=['GET'])
def get_latest_prediction():
    """Get the latest prediction for the dashboard"""
    global latest_prediction
    return jsonify(latest_prediction)

if __name__ == '__main__':
    # Runs the server on 0.0.0.0 to be accessible from the network.
    # Make sure your firewall allows connections on this port.
    app.run(host='0.0.0.0', port=5000, debug=True)
