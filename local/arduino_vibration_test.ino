/*
 * Vibration Sensor Test for Arduino
 * 
 * Connections:
 * Vibration Sensor VCC (+) -> Arduino 5V (or 3.3V)
 * Vibration Sensor GND (-) -> Arduino GND
 * Vibration Sensor SIG (S) -> Arduino A3
 */

// Analog pin for vibration sensor
const int vibPin = A3;

// Variables for readings
int currentReading = 0;
int baseline = 0;
int threshold = 50;  // Adjust this based on your sensor sensitivity
bool calibrated = false;

void setup() {
  Serial.begin(9600);
  Serial.println("Vibration Sensor Test");
  Serial.println("Calibrating baseline... Keep sensor still!");
  
  // Calibrate baseline (average of first 20 readings)
  long total = 0;
  for(int i = 0; i < 20; i++) {
    total += analogRead(vibPin);
    delay(100);
  }
  baseline = total / 20;
  
  Serial.print("Baseline calibrated: ");
  Serial.print(baseline);
  Serial.print(" (");
  Serial.print((baseline * 5.0) / 1023.0, 2);
  Serial.println("V)");
  Serial.println("Ready! Tap or shake the sensor...");
  Serial.println("Raw | Voltage | Delta | Status");
  Serial.println("--------------------------------");
  
  calibrated = true;
}

void loop() {
  // Read current value
  currentReading = analogRead(vibPin);
  
  // Convert to voltage
  float voltage = (currentReading * 5.0) / 1023.0;
  
  // Calculate difference from baseline
  int delta = abs(currentReading - baseline);
  
  // Determine vibration level
  String status;
  if (delta < threshold) {
    status = "No Vibration";
  } else if (delta < threshold * 2) {
    status = "Light Vibration";
  } else if (delta < threshold * 4) {
    status = "Moderate Vibration";
  } else {
    status = "Strong Vibration";
  }
  
  // Print results
  Serial.print(currentReading);
  Serial.print(" | ");
  Serial.print(voltage, 2);
  Serial.print("V | ");
  Serial.print(delta);
  Serial.print(" | ");
  Serial.println(status);
  
  delay(100); // Fast updates to catch vibrations
}

/*
 * Troubleshooting:
 * 
 * 1. If readings are always 0 or 1023:
 *    - Check wiring (VCC, GND, Signal)
 *    - Try different analog pin
 * 
 * 2. If no vibration detected:
 *    - Lower the threshold value (try 20 or 10)
 *    - Check if sensor requires 5V instead of 3.3V
 * 
 * 3. If too sensitive:
 *    - Increase threshold value (try 100 or 200)
 * 
 * 4. Expected behavior:
 *    - Steady reading when still
 *    - Sudden changes when tapped/shaken
 *    - Returns to baseline when vibration stops
 */
