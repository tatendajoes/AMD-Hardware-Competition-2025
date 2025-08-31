# Sensor Wiring Guide for Red Pitaya STEMlab 125-14

This document provides the exact pin connections for the ADXL335 accelerometer and the analog vibration sensor.

**Reference Connectors on Red Pitaya:**
- **E1 (Power & Digital I/O):** Used for providing power (3.3V) and ground (GND).
- **E2 (Analog & Digital I/O):** Used for reading the analog signals from the sensors.

---

### 1. ADXL335 Accelerometer (Analog)

This sensor has 7 pins total, but we only need to connect 5 for basic operation.

**Required Connections:**
| ADXL335 Pin | -> | Red Pitaya Pin      | Details                               |
|-------------|----|---------------------|---------------------------------------|
| **VCC**     | -> | **E1, Pin 1**       | 3.3V Power Supply                     |
| **GND**     | -> | **E1, Pin 9**       | Ground                                |
| **Xout**    | -> | **E2, Pin 11 (AIN0)** | Analog Input for X-axis               |
| **Yout**    | -> | **E2, Pin 12 (AIN1)** | Analog Input for Y-axis               |
| **Zout**    | -> | **E2, Pin 13 (AIN2)** | Analog Input for Z-axis               |

**Optional Connections (can be left unconnected for basic operation):**
| ADXL335 Pin | -> | Connection          | Details                               |
|-------------|----|---------------------|---------------------------------------|
| **ST**      | -> | Not connected       | Self-test pin (optional)              |
| **COM**     | -> | Not connected       | Common reference (typically VCC/2)    |

---

### 2. Vibration Sensor Disk (Analog)

This sensor outputs a single analog voltage that corresponds to the amount of vibration it detects.

**Connections:**
| Vibration Sensor Pin | -> | Red Pitaya Pin      | Details           |
|----------------------|----|---------------------|-------------------|
| **+ (or VCC)**       | -> | **E1, Pin 1**       | 3.3V Power Supply |
| **- (or GND)**       | -> | **E1, Pin 9**       | Ground            |
| **S (or Signal)**    | -> | **E2, Pin 14 (AIN3)** | Analog Signal Out |

---

### Summary of Red Pitaya Pins Used:

- **3.3V Power:** `E1, Pin 1` (Shared by both sensors)
- **Ground:** `E1, Pin 9` (Shared by both sensors)
- **Analog Input 0 (AIN0):** `E2, Pin 11` (Accelerometer X)
- **Analog Input 1 (AIN1):** `E2, Pin 12` (Accelerometer Y)
- **Analog Input 2 (AIN2):** `E2, Pin 13` (Accelerometer Z)
- **Analog Input 3 (AIN3):** `E2, Pin 14` (Vibration Sensor Signal)
