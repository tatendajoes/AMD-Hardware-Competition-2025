# Red Pitaya and Signal Collection

## Overview
This section details the hardware platform, sensor integration, and signal acquisition methodology used for collecting vibration and acceleration data. The system leverages the Red Pitaya STEMlab 125-14 as the primary data acquisition platform, with Arduino used for sensor validation and calibration.

## Red Pitaya STEMlab 125-14 Platform

### Hardware Specifications
The Red Pitaya STEMlab 125-14 serves as the core data acquisition system with the following key specifications:

**Processing Unit:**
- ARM Cortex-A9 dual-core processor @ 866 MHz
- 512 MB DDR3 RAM
- Embedded Linux operating system (Ubuntu-based)
- Built-in Python 3 environment

**Analog Input Capabilities:**
- 4 × Fast analog inputs (AIN0-AIN3)
- Input voltage range: ±1V differential, ±20V common mode
- 14-bit resolution (16,384 discrete levels)
- Maximum sampling rate: 125 MS/s
- Input impedance: 1 MΩ || 10 pF

**Digital I/O:**
- GPIO pins for digital control
- 3.3V and 5V power output pins for sensor power supply
- Ground connections for complete circuit integration

**Connectivity:**
- Ethernet port for network communication
- SSH access for remote programming and control
- Web interface for configuration and monitoring

### Red Pitaya Software Tools and Libraries

**Native Python Library (`rp`):**
- Location: `/opt/redpitaya/lib/python/rp`
- Provides direct hardware access to analog inputs
- Key functions utilized:
  - `rp.rp_Init()`: Initialize Red Pitaya hardware
  - `rp.rp_AIpinGetValue()`: Read analog input voltages
  - `rp.rp_Release()`: Clean up hardware resources

**Development Environment:**
- SSH terminal access via `ssh root@rp-f0d25d.local`
- Python 3 scripting environment
- Real-time data acquisition capabilities
- Network-based data transmission

## Sensor Hardware Configuration

### ADXL335 Accelerometer
**Specifications:**
- 3-axis analog accelerometer
- Measurement range: ±3g on all axes
- Sensitivity: ~300 mV/g (nominal)
- Supply voltage: 1.8V to 3.6V (powered from Red Pitaya 3.3V)
- Output: Analog voltage proportional to acceleration

**Pin Configuration:**
- 7-pin module layout: `Vin | 3Vo | Zout | Yout | Xout | Test`
- Connections to Red Pitaya:
  - VCC → Red Pitaya 3.3V pin
  - GND → Red Pitaya Ground
  - X-axis → AIN0 (analog input 0)
  - Y-axis → AIN1 (analog input 1)  
  - Z-axis → AIN2 (analog input 2)

### Analog Vibration Sensor
**Specifications:**
- Piezoelectric vibration detection
- 3-pin configuration: Power (+), Ground (-), Signal (S)
- Output: Analog voltage varying with vibration intensity
- Supply voltage: 3.3V to 5V

**Connection:**
- VCC → Red Pitaya 3.3V pin
- GND → Red Pitaya Ground  
- Signal → AIN3 (analog input 3)

## Signal Collection Methodology

### Voltage Compatibility Considerations
**Challenge:** Red Pitaya analog inputs accept maximum ±1V, while sensors can output 0-3.3V signals.

**Solution:** Power sensors from Red Pitaya's 3.3V supply instead of 5V to scale output voltages within acceptable range.

**Voltage Scaling:**
- 3.3V supply → sensor outputs: 0V to 3.3V theoretical maximum
- Actual accelerometer outputs: ~1.0V to 2.2V (within safe range after voltage divider effect)
- Red Pitaya input protection handles minor overages gracefully

### Arduino-Based Sensor Validation

**Purpose:** Validate sensor functionality and determine calibration parameters before Red Pitaya integration.

**Arduino Uno Specifications:**
- 10-bit ADC (1024 discrete levels)
- 5V supply and analog reference
- Real-time serial output for monitoring

**Validation Process:**
1. **Sensor Connectivity Test:** Verify all sensor channels respond to physical stimuli
2. **Calibration Determination:** 
   - Measure zero-g bias voltage for accelerometer axes
   - Determine sensitivity (mV/g) through orientation testing
   - Establish vibration sensor baseline and threshold levels
3. **Signal Quality Assessment:** Monitor for noise, drift, and linearity

**Calibration Results (Arduino @ 5V):**
- Zero-g bias: 1.65V (scaled to 1.09V for Red Pitaya @ 3.3V)
- Sensitivity: 0.22 V/g (scaled to 0.145 V/g for Red Pitaya)
- Vibration baseline: Auto-calibrated during initialization

### Red Pitaya Data Acquisition Implementation

**Software Architecture:**
```python
# Core acquisition loop structure
rp.rp_Init()  # Initialize hardware
while collecting:
    x_volt = rp.rp_AIpinGetValue(rp.RP_AIN0)[1]  # Read X-axis
    y_volt = rp.rp_AIpinGetValue(rp.RP_AIN1)[1]  # Read Y-axis  
    z_volt = rp.rp_AIpinGetValue(rp.RP_AIN2)[1]  # Read Z-axis
    vib_volt = rp.rp_AIpinGetValue(rp.RP_AIN3)[1]  # Read vibration
    # Convert to engineering units and process
rp.rp_Release()  # Clean up
```

**Sampling Strategy:**
- Configurable sampling rates up to 1 kHz for real-time applications
- Windowed data collection (typically 250-1000 samples per analysis window)
- Synchronized multi-channel acquisition across all four sensor channels

**Signal Processing Pipeline:**
1. **Raw Voltage Acquisition:** Direct ADC readings from all sensor channels
2. **Engineering Unit Conversion:** Apply calibration factors to convert voltages to g-forces and vibration levels
3. **Feature Extraction:** Calculate 8 statistical features per sensor channel:
   - RMS (Root Mean Square)
   - Peak value
   - Mean
   - Standard deviation
   - Kurtosis (peakiness measure)
   - Skewness (asymmetry measure)
   - Crest factor (peak/RMS ratio)
   - Shannon entropy (signal complexity)

### Data Transmission Architecture

**Network Communication:**
- Red Pitaya connects via Ethernet to host network
- RESTful API communication using HTTP POST requests
- JSON payload format for feature vector transmission

**Data Flow:**
```
Sensors → Red Pitaya ADC → Feature Extraction → JSON Encoding → HTTP POST → Web Server → ML Model
```

**Payload Structure:**
- 32 total features (4 sensors × 8 features each)
- Metadata including sampling rate, window size, and timestamps
- Error handling and retry mechanisms for network reliability

## System Integration Benefits

**Real-time Capabilities:**
- Sub-millisecond sensor response times
- Continuous data streaming capability
- Low-latency network transmission

**Scalability:**
- Modular sensor integration (easy to add additional channels)
- Configurable sampling parameters
- Remote monitoring and control capabilities

**Research Flexibility:**
- Open-source software stack
- Custom algorithm development
- Integration with external analysis tools

This signal collection architecture provides a robust foundation for machine learning applications requiring high-quality, multi-channel sensor data with real-time processing capabilities.
