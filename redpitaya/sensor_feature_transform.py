# AMD-Hardware-Competition-2025/redpitaya/sensor_feature_transform.py

import numpy as np
import math
from scipy import stats
from scipy.stats import entropy
import json
import time

class SensorFeatureTransform:
    """
    Transform raw sensor data into exactly 8 required features per sensor:
    1. RMS (Root Mean Square)
    2. Peak 
    3. Mean
    4. Standard Deviation
    5. Kurtosis
    6. Skewness  
    7. Crest Factor
    8. Entropy
    """
    
    def extract_8_features(self, data):
        """
        Extract exactly 8 features from sensor data array
        :param data: numpy array of sensor readings
        :return: dictionary with exactly 8 features
        """
        data = np.array(data, dtype=float)
        
        # 1. RMS (Root Mean Square) - sqrt(mean(data²))
        rms = np.sqrt(np.mean(data**2))
        
        # 2. Peak - max(abs(data))
        peak = np.max(np.abs(data))
        
        # 3. Mean - mean(data)
        mean = np.mean(data)
        
        # 4. Standard Deviation - std(data)
        std_dev = np.std(data)
        
        # 5. Kurtosis - measure of peakiness
        kurtosis = stats.kurtosis(data) if len(data) > 1 and std_dev > 0 else 0.0
        
        # 6. Skewness - measure of asymmetry
        skewness = stats.skew(data) if len(data) > 1 and std_dev > 0 else 0.0
        
        # 7. Crest Factor - peak / rms
        crest_factor = peak / rms if rms > 0 else 0.0
        
        # 8. Entropy - Shannon entropy of data distribution
        # Create histogram for entropy calculation
        if len(data) > 1:
            hist, _ = np.histogram(data, bins=min(50, len(data)//2), density=True)
            # Remove zeros and normalize
            hist = hist[hist > 0]
            if len(hist) > 1:
                hist = hist / np.sum(hist)
                shannon_entropy = entropy(hist)
            else:
                shannon_entropy = 0.0
        else:
            shannon_entropy = 0.0
        
        return {
            'rms': float(rms),
            'peak': float(peak),
            'mean': float(mean),
            'std_dev': float(std_dev),
            'kurtosis': float(kurtosis),
            'skewness': float(skewness),
            'crest_factor': float(crest_factor),
            'entropy': float(shannon_entropy)
        }
    
    def collect_and_transform_sensors(self, accelerometer, vibration_sensor, window_size=500):
        """
        Collect sensor data and transform to feature vectors
        :param accelerometer: Accelerometer object
        :param vibration_sensor: VibrationSensor object  
        :param window_size: Number of samples to collect
        :return: Dictionary with 8 features per sensor (32 features total)
        """
        print(f"Collecting {window_size} samples for feature extraction...")
        
        # Initialize data arrays
        accel_x_data = []
        accel_y_data = []
        accel_z_data = []
        vibration_data = []
        
        # Collect sensor readings
        start_time = time.time()
        for i in range(window_size):
            try:
                # Read accelerometer
                x_g, y_g, z_g = accelerometer.get_g_force()
                accel_x_data.append(x_g)
                accel_y_data.append(y_g)
                accel_z_data.append(z_g)
                
                # Read vibration sensor  
                vib_level = vibration_sensor.get_vibration_level()
                vibration_data.append(vib_level)
                
            except Exception as e:
                print(f"Sensor read error: {e}")
                # Use last known values or zeros
                accel_x_data.append(accel_x_data[-1] if accel_x_data else 0.0)
                accel_y_data.append(accel_y_data[-1] if accel_y_data else 0.0)
                accel_z_data.append(accel_z_data[-1] if accel_z_data else 0.0)
                vibration_data.append(vibration_data[-1] if vibration_data else 0.0)
            
            # Simple delay for sampling rate control
            time.sleep(0.001)  # 1ms = ~1000Hz max
        
        collection_time = time.time() - start_time
        actual_rate = window_size / collection_time
        print(f"Data collected in {collection_time:.2f}s (≈{actual_rate:.0f}Hz)")
        
        # Transform each sensor to 8 features
        features = {
            'accelerometer_x': self.extract_8_features(accel_x_data),
            'accelerometer_y': self.extract_8_features(accel_y_data),
            'accelerometer_z': self.extract_8_features(accel_z_data),
            'vibration': self.extract_8_features(vibration_data)
        }
        
        # Add metadata
        features['metadata'] = {
            'window_size': window_size,
            'collection_time': collection_time,
            'sampling_rate': actual_rate,
            'timestamp': time.time()
        }
        
        return features
    
    def format_for_web_server(self, features):
        """
        Format features for posting to web server
        :param features: Dictionary from collect_and_transform_sensors()
        :return: JSON-ready dictionary
        """
        # Create flattened feature vector with clear naming
        web_data = {
            'timestamp': features['metadata']['timestamp'],
            'sampling_info': {
                'window_size': features['metadata']['window_size'],
                'sampling_rate': features['metadata']['sampling_rate']
            },
            'sensor_features': {
                # Accelerometer X features (8)
                'accel_x_rms': features['accelerometer_x']['rms'],
                'accel_x_peak': features['accelerometer_x']['peak'],
                'accel_x_mean': features['accelerometer_x']['mean'],
                'accel_x_std_dev': features['accelerometer_x']['std_dev'],
                'accel_x_kurtosis': features['accelerometer_x']['kurtosis'],
                'accel_x_skewness': features['accelerometer_x']['skewness'],
                'accel_x_crest_factor': features['accelerometer_x']['crest_factor'],
                'accel_x_entropy': features['accelerometer_x']['entropy'],
                
                # Accelerometer Y features (8)
                'accel_y_rms': features['accelerometer_y']['rms'],
                'accel_y_peak': features['accelerometer_y']['peak'],
                'accel_y_mean': features['accelerometer_y']['mean'],
                'accel_y_std_dev': features['accelerometer_y']['std_dev'],
                'accel_y_kurtosis': features['accelerometer_y']['kurtosis'],
                'accel_y_skewness': features['accelerometer_y']['skewness'],
                'accel_y_crest_factor': features['accelerometer_y']['crest_factor'],
                'accel_y_entropy': features['accelerometer_y']['entropy'],
                
                # Accelerometer Z features (8) 
                'accel_z_rms': features['accelerometer_z']['rms'],
                'accel_z_peak': features['accelerometer_z']['peak'],
                'accel_z_mean': features['accelerometer_z']['mean'],
                'accel_z_std_dev': features['accelerometer_z']['std_dev'],
                'accel_z_kurtosis': features['accelerometer_z']['kurtosis'],
                'accel_z_skewness': features['accelerometer_z']['skewness'],
                'accel_z_crest_factor': features['accelerometer_z']['crest_factor'],
                'accel_z_entropy': features['accelerometer_z']['entropy'],
                
                # Vibration sensor features (8)
                'vibration_rms': features['vibration']['rms'],
                'vibration_peak': features['vibration']['peak'],
                'vibration_mean': features['vibration']['mean'],
                'vibration_std_dev': features['vibration']['std_dev'],
                'vibration_kurtosis': features['vibration']['kurtosis'],
                'vibration_skewness': features['vibration']['skewness'],
                'vibration_crest_factor': features['vibration']['crest_factor'],
                'vibration_entropy': features['vibration']['entropy']
            }
        }
        
        return web_data
    
    def print_feature_summary(self, features):
        """Print features in a readable format"""
        sensors = ['accelerometer_x', 'accelerometer_y', 'accelerometer_z', 'vibration']
        feature_names = ['rms', 'peak', 'mean', 'std_dev', 'kurtosis', 'skewness', 'crest_factor', 'entropy']
        
        print("\n" + "="*80)
        print("SENSOR FEATURE EXTRACTION SUMMARY")
        print("="*80)
        
        for sensor in sensors:
            print(f"\n{sensor.upper()} (8 features):")
            print("-" * 40)
            for i, feature in enumerate(feature_names, 1):
                value = features[sensor][feature]
                print(f"  {i}. {feature:12s}: {value:10.4f}")
        
        print(f"\nMetadata:")
        print(f"  Window size: {features['metadata']['window_size']}")
        print(f"  Sampling rate: {features['metadata']['sampling_rate']:.1f} Hz")
        print(f"  Collection time: {features['metadata']['collection_time']:.2f}s")
        print("\nTotal features: 32 (4 sensors × 8 features each)")
        print("="*80)

if __name__ == '__main__':
    # Example usage
    try:
        import sys
        sys.path.append('/opt/redpitaya/lib/python')
        import rp
        
        # Initialize Red Pitaya
        rp.rp_Init()
        print("Red Pitaya initialized for feature transformation!")
        
        # Import sensor classes
        from sensors.accelerometer import Accelerometer
        from sensors.vibration_sensor import VibrationSensor
        
        # Create sensor objects
        accel = Accelerometer()
        vib_sensor = VibrationSensor()
        
        # Create feature transformer
        transformer = SensorFeatureTransform()
        
        print("Starting sensor data transformation...")
        print("Raw sensor data → 8 features per sensor → 32 total features")
        
        while True:
            # Collect and transform sensor data
            features = transformer.collect_and_transform_sensors(accel, vib_sensor, window_size=250)
            
            # Print summary
            transformer.print_feature_summary(features)
            
            # Format for web server
            web_data = transformer.format_for_web_server(features)
            print(f"\nJSON payload ready: {len(json.dumps(web_data))} bytes")
            
            # Wait before next collection
            time.sleep(3)
    
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            rp.rp_Release()
            print("Red Pitaya resources released.")
        except:
            pass
