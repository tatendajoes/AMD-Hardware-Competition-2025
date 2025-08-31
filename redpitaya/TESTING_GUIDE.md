# AMD-Hardware-Competition-2025/redpitaya/TESTING_GUIDE.md

# RedPitaya Sensor Testing Guide

## Quick Start Testing

### 1. Run Comprehensive Test
```bash
cd /opt/redpitaya/
python3 test_complete_system.py
```

### 2. Run Basic Working Test
```bash
python3 test_sensors_working.py
```

### 3. Test Individual Components
```bash
# Test just the accelerometer
python3 -c "from sensors.accelerometer import Accelerometer; import rp; rp.rp_Init(); a=Accelerometer(); print(a.get_g_force())"

# Test just the vibration sensor
python3 -c "from sensors.vibration_sensor import VibrationSensor; import rp; rp.rp_Init(); v=VibrationSensor(); print(v.get_vibration_level())"
```

## Expected Results

### Accelerometer (ADXL335)
- **At rest on flat surface**: Z should read ~+1.0g, X and Y near 0g
- **Tilted 90°**: One axis should read ±1.0g depending on orientation
- **Values should be between -3g and +3g** (ADXL335 range)

### Vibration Sensor
- **Quiet environment**: Low voltage (< 0.5V typically)
- **With vibration/movement**: Higher voltage readings
- **Should respond to tapping/movement**

## Troubleshooting

### Import Errors
```bash
# Check if RedPitaya library exists
ls -la /opt/redpitaya/lib/python/
# Should show 'rp.so' or similar files

# Install missing packages
pip3 install requests numpy
```

### Connection Issues
```bash
# Check if running on RedPitaya
uname -a
# Should show something like "armv7l" and "Red Pitaya"

# Restart Red Pitaya services
systemctl restart redpitaya_scpi
```

### Hardware Issues
1. **Check connections** - refer to SENSOR_WIRING.md
2. **Verify power** - sensors should have 3.3V supply
3. **Test with multimeter** - manually verify voltage levels

### Calibration Issues
- The accelerometer should read approximately 1g on Z-axis when lying flat
- If readings are way off, you may need to adjust calibration constants
- Compare with Arduino readings if available

## Known Issues

1. **Calibration Inconsistency**: Main code and test files use different calibration values
2. **Library Path**: May need adjustment depending on RedPitaya OS version
3. **Data Posting**: Currently commented out in main acquisition loop

## Next Steps After Testing

1. If hardware tests pass → Run full data acquisition
2. If calibration is off → Adjust constants in accelerometer.py
3. If ready for integration → Uncomment data posting in data_acquisition.py
