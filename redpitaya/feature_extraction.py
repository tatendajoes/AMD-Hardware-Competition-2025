# AMD-Hardware-Competition-2025/redpitaya/feature_extraction.py

import numpy as np
import math
from scipy import stats
from scipy.stats import entropy
import sys
import time

# Add Red Pitaya library path
sys.path.append('/opt/redpitaya/lib/python')
import rp

class FeatureExtractor:
    """
    Extract statistical features from sensor time series data
    Includes: RMS, Peak, Entropy, Kurtosis, Crest Factor, Mean, Skewness, Standard Deviation
    """
    
    def __init__(self, window_size=1000, sampling_rate=1000):
        """
        Initialize feature extractor
        :param window_size: Number of samples to collect for feature calculation
        :param sampling_rate: Sampling rate in Hz
        """
        self.window_size = window_size
        self.sampling_rate = sampling_rate
        self.sampling_period = 1.0 / sampling_rate  # Time between samples
        
    def extract_time_domain_features(self, data):
        """
        Extract time domain statistical features from sensor data
        :param data: numpy array of sensor readings
        :return: dictionary of features
        """
        features = {}
        
        # Convert to numpy array if not already
        data = np.array(data)
        
        # Basic statistics
        features['mean'] = np.mean(data)
        features['std'] = np.std(data)
        features['variance'] = np.var(data)
        
        # RMS (Root Mean Square) - overall energy
        features['rms'] = np.sqrt(np.mean(data**2))
        
        # Peak values
        features['peak'] = np.max(np.abs(data))
        features['peak_to_peak'] = np.max(data) - np.min(data)
        features['max'] = np.max(data)
        features['min'] = np.min(data)
        
        # Crest Factor (Peak/RMS) - indicates impulsiveness
        if features['rms'] > 0:
            features['crest_factor'] = features['peak'] / features['rms']
        else:
            features['crest_factor'] = 0
            
        # Shape statistics
        if len(data) > 1 and features['std'] > 0:
            features['skewness'] = stats.skew(data)
            features['kurtosis'] = stats.kurtosis(data)
        else:
            features['skewness'] = 0
            features['kurtosis'] = 0
            
        return features
    
    def extract_frequency_domain_features(self, data):
        """
        Extract frequency domain features
        :param data: numpy array of sensor readings
        :return: dictionary of features
        """
        features = {}
        
        # Convert to numpy array
        data = np.array(data)
        
        # FFT for frequency analysis
        fft = np.fft.fft(data)
        freqs = np.fft.fftfreq(len(data), self.sampling_period)
        
        # Power spectral density
        psd = np.abs(fft)**2
        
        # Normalize PSD for entropy calculation
        psd_norm = psd / np.sum(psd)
        
        # Spectral entropy - measure of signal complexity
        # Remove zero values to avoid log(0)
        psd_nonzero = psd_norm[psd_norm > 0]
        if len(psd_nonzero) > 0:
            features['spectral_entropy'] = entropy(psd_nonzero)
        else:
            features['spectral_entropy'] = 0
            
        # Dominant frequency
        dominant_freq_idx = np.argmax(psd[:len(psd)//2])  # Only positive frequencies
        features['dominant_frequency'] = abs(freqs[dominant_freq_idx])
        
        return features
    
    def extract_all_features(self, data):
        """
        Extract both time and frequency domain features
        :param data: numpy array of sensor readings
        :return: combined dictionary of all features
        """
        time_features = self.extract_time_domain_features(data)
        freq_features = self.extract_frequency_domain_features(data)
        
        # Combine dictionaries
        all_features = {**time_features, **freq_features}
        
        return all_features
    
    def collect_sensor_window(self, accelerometer, vibration_sensor):
        """
        Collect a window of sensor data for feature extraction
        :param accelerometer: Accelerometer object
        :param vibration_sensor: VibrationSensor object
        :return: dictionary with sensor data arrays
        """
        # Initialize data storage
        accel_x = []
        accel_y = []
        accel_z = []
        vibration = []
        timestamps = []
        
        print(f"Collecting {self.window_size} samples at {self.sampling_rate}Hz...")
        
        start_time = time.time()
        for i in range(self.window_size):
            sample_start = time.time()
            
            # Read accelerometer
            try:
                x_g, y_g, z_g = accelerometer.get_g_force()
                accel_x.append(x_g)
                accel_y.append(y_g)
                accel_z.append(z_g)
            except Exception as e:
                print(f"Accelerometer read error: {e}")
                accel_x.append(0)
                accel_y.append(0)
                accel_z.append(0)
            
            # Read vibration sensor
            try:
                vib_level = vibration_sensor.get_vibration_level()
                vibration.append(vib_level)
            except Exception as e:
                print(f"Vibration sensor read error: {e}")
                vibration.append(0)
            
            timestamps.append(time.time() - start_time)
            
            # Maintain sampling rate
            elapsed = time.time() - sample_start
            sleep_time = self.sampling_period - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        total_time = time.time() - start_time
        actual_rate = self.window_size / total_time
        print(f"Actual sampling rate: {actual_rate:.1f}Hz")
        
        return {
            'accel_x': np.array(accel_x),
            'accel_y': np.array(accel_y), 
            'accel_z': np.array(accel_z),
            'vibration': np.array(vibration),
            'timestamps': np.array(timestamps),
            'sampling_rate': actual_rate
        }
    
    def analyze_sensor_data(self, accelerometer, vibration_sensor):
        """
        Complete feature extraction pipeline
        :param accelerometer: Accelerometer object
        :param vibration_sensor: VibrationSensor object
        :return: dictionary with features for each sensor axis
        """
        # Collect sensor data
        sensor_data = self.collect_sensor_window(accelerometer, vibration_sensor)
        
        # Extract features for each sensor channel
        results = {}
        
        # Accelerometer features
        results['accel_x_features'] = self.extract_all_features(sensor_data['accel_x'])
        results['accel_y_features'] = self.extract_all_features(sensor_data['accel_y'])
        results['accel_z_features'] = self.extract_all_features(sensor_data['accel_z'])
        
        # Vibration sensor features
        results['vibration_features'] = self.extract_all_features(sensor_data['vibration'])
        
        # Combined accelerometer magnitude
        accel_magnitude = np.sqrt(sensor_data['accel_x']**2 + 
                                 sensor_data['accel_y']**2 + 
                                 sensor_data['accel_z']**2)
        results['accel_magnitude_features'] = self.extract_all_features(accel_magnitude)
        
        # Add metadata
        results['metadata'] = {
            'window_size': self.window_size,
            'target_sampling_rate': self.sampling_rate,
            'actual_sampling_rate': sensor_data['sampling_rate'],
            'total_duration': sensor_data['timestamps'][-1]
        }
        
        return results

def print_features(features, sensor_name):
    """Helper function to print features in a readable format"""
    print(f"\n{sensor_name} Features:")
    print("=" * 50)
    
    time_domain = ['mean', 'std', 'variance', 'rms', 'peak', 'peak_to_peak', 
                   'max', 'min', 'crest_factor', 'skewness', 'kurtosis']
    freq_domain = ['spectral_entropy', 'dominant_frequency']
    
    print("Time Domain:")
    for feature in time_domain:
        if feature in features:
            print(f"  {feature}: {features[feature]:.4f}")
    
    print("Frequency Domain:")
    for feature in freq_domain:
        if feature in features:
            print(f"  {feature}: {features[feature]:.4f}")

if __name__ == '__main__':
    # Example usage
    try:
        # Initialize Red Pitaya
        rp.rp_Init()
        print("Red Pitaya initialized for feature extraction!")
        
        # Import sensor classes
        from sensors.accelerometer import Accelerometer
        from sensors.vibration_sensor import VibrationSensor
        
        # Create sensor objects
        accel = Accelerometer()
        vib_sensor = VibrationSensor()
        
        # Create feature extractor (1 second of data at 500Hz)
        extractor = FeatureExtractor(window_size=500, sampling_rate=500)
        
        print("Starting feature extraction...")
        print("Place sensors in different conditions to see feature changes!")
        
        while True:
            # Extract features
            results = extractor.analyze_sensor_data(accel, vib_sensor)
            
            # Print results
            print_features(results['accel_x_features'], "Accelerometer X")
            print_features(results['accel_y_features'], "Accelerometer Y") 
            print_features(results['accel_z_features'], "Accelerometer Z")
            print_features(results['vibration_features'], "Vibration Sensor")
            print_features(results['accel_magnitude_features'], "Accelerometer Magnitude")
            
            print(f"\nMetadata: {results['metadata']}")
            print("\n" + "="*80 + "\n")
            
            # Wait before next analysis
            time.sleep(2)
    
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
