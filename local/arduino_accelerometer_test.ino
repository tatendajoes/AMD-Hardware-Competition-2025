/*
 * ADXL335 Accelerometer Test for Arduino
 * 
 * Your ADXL335 module pinout: Vin | 3Vo | Zout | Yout | Xout | Test
 * 
 * Connections:
 * ADXL335 Vin   -> Arduino 5V (or 3.3V)
 * ADXL335 3Vo   -> Not connected (this is a 3V output from module)
 * ADXL335 Zout  -> Arduino A2
 * ADXL335 Yout  -> Arduino A1  
 * ADXL335 Xout  -> Arduino A0
 * ADXL335 Test  -> Not connected (self-test pin)
 * 
 * Also connect: ADXL335 GND -> Arduino GND (if there's a GND pin)
 */

// Analog pins for accelerometer
const int xPin = A0;
const int yPin = A1;
const int zPin = A2;

// Calibration values - CORRECTED for your specific ADXL335 module
float vcc = 5.0;           // Arduino supply voltage
float zeroG = 1.9;         // Based on your X/Y readings (~1.89V, 1.98V when flat)
float sensitivity = 0.33;  // Adjusted sensitivity - we'll fine-tune this

void setup() {
  Serial.begin(9600);
  Serial.println("ADXL335 Accelerometer Test");
  Serial.println("Place sensor flat on table for calibration reference");
  Serial.println("Expected: X≈0g, Y≈0g, Z≈1g");
  Serial.println("Raw | Voltage | G-force");
  Serial.println("------------------------");
  delay(2000);
}

void loop() {
  // Read raw ADC values (0-1023 for 10-bit ADC)
  int xRaw = analogRead(xPin);
  int yRaw = analogRead(yPin);
  int zRaw = analogRead(zPin);
  
  // Convert to voltage (0-5V for Arduino Uno)
  float xVolt = (xRaw * vcc) / 1023.0;
  float yVolt = (yRaw * vcc) / 1023.0;
  float zVolt = (zRaw * vcc) / 1023.0;
  
  // Convert to g-force
  float xG = (xVolt - zeroG) / sensitivity;
  float yG = (yVolt - zeroG) / sensitivity;
  float zG = (zVolt - zeroG) / sensitivity;
  
  // Print results
  Serial.print("X: ");
  Serial.print(xRaw); Serial.print(" | ");
  Serial.print(xVolt, 2); Serial.print("V | ");
  Serial.print(xG, 2); Serial.print("g   ");
  
  Serial.print("Y: ");
  Serial.print(yRaw); Serial.print(" | ");
  Serial.print(yVolt, 2); Serial.print("V | ");
  Serial.print(yG, 2); Serial.print("g   ");
  
  Serial.print("Z: ");
  Serial.print(zRaw); Serial.print(" | ");
  Serial.print(zVolt, 2); Serial.print("V | ");
  Serial.print(zG, 2); Serial.println("g");
  
  delay(500); // Update every 500ms
}

/*
 * Calibration Notes:
 * 1. With sensor flat on table, Z should read close to 1g (gravity)
 * 2. X and Y should read close to 0g
 * 3. If readings are off, adjust these values:
 *    - zeroG: The voltage when sensor reads 0g (usually VCC/2)
 *    - sensitivity: How much voltage changes per g (usually 0.3V/g)
 * 
 * Example calibration:
 * If Z reads 2.5V when flat, and should be 1g:
 * Then 1.5V difference from zeroG (2.5V) = 1g
 * So sensitivity = 1.0V / 1g = 1.0 (instead of 0.3)
 */
