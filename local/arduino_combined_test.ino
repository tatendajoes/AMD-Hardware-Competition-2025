/*
 * Combined Sensor Test for Arduino
 * Tests both ADXL335 Accelerometer and Vibration Sensor
 * 
 * Connections:
 * ADXL335 VCC  -> Arduino 5V
 * ADXL335 GND  -> Arduino GND
 * ADXL335 X    -> Arduino A0
 * ADXL335 Y    -> Arduino A1
 * ADXL335 Z    -> Arduino A2
 * 
 * Vibration VCC -> Arduino 5V
 * Vibration GND -> Arduino GND
 * Vibration SIG -> Arduino A3
 */

// Pin definitions
const int xPin = A0;
const int yPin = A1;
const int zPin = A2;
const int vibPin = A3;

// Accelerometer calibration - CORRECTED based on your readings
float vcc = 5.0;
float zeroG = 1.65;       // Adjusted for 0g readings on X/Y
float sensitivity = 0.22;  // Increased sensitivity for proper scaling

// Vibration sensor calibration
int vibBaseline = 0;
int vibThreshold = 50;

void setup() {
  Serial.begin(9600);
  Serial.println("=== Combined Sensor Test ===");
  Serial.println("ADXL335 + Vibration Sensor");
  
  // Calibrate vibration sensor baseline
  Serial.println("Calibrating vibration baseline...");
  long total = 0;
  for(int i = 0; i < 20; i++) {
    total += analogRead(vibPin);
    delay(50);
  }
  vibBaseline = total / 20;
  
  Serial.print("Vibration baseline: ");
  Serial.println(vibBaseline);
  Serial.println("Ready!");
  Serial.println();
  delay(1000);
}

void loop() {
  // Read accelerometer
  int xRaw = analogRead(xPin);
  int yRaw = analogRead(yPin);
  int zRaw = analogRead(zPin);
  
  float xVolt = (xRaw * vcc) / 1023.0;
  float yVolt = (yRaw * vcc) / 1023.0;
  float zVolt = (zRaw * vcc) / 1023.0;
  
  float xG = (xVolt - zeroG) / sensitivity;
  float yG = (yVolt - zeroG) / sensitivity;
  float zG = (zVolt - zeroG) / sensitivity;
  
  // Read vibration sensor
  int vibRaw = analogRead(vibPin);
  float vibVolt = (vibRaw * vcc) / 1023.0;
  int vibDelta = abs(vibRaw - vibBaseline);
  
  String vibStatus;
  if (vibDelta < vibThreshold) {
    vibStatus = "Still";
  } else if (vibDelta < vibThreshold * 2) {
    vibStatus = "Light";
  } else {
    vibStatus = "Strong";
  }
  
  // Print combined results
  Serial.print("Accel: X=");
  Serial.print(xG, 1);
  Serial.print("g Y=");
  Serial.print(yG, 1);
  Serial.print("g Z=");
  Serial.print(zG, 1);
  Serial.print("g | Vib: ");
  Serial.print(vibVolt, 2);
  Serial.print("V (");
  Serial.print(vibStatus);
  Serial.println(")");
  
  delay(300);
}

/*
 * What to expect:
 * 1. Accelerometer flat on table: X≈0g, Y≈0g, Z≈1g
 * 2. Tilt sensor: readings should change accordingly
 * 3. Vibration: should show "Still" normally, "Light" or "Strong" when tapped
 * 
 * This will help verify both sensors work before connecting to Red Pitaya!
 */
