/*
 * ADXL335 Calibration Script for Arduino
 * This will help determine the correct zeroG and sensitivity values
 * 
 * Instructions:
 * 1. Upload this script
 * 2. Place sensor flat on table (Z pointing up)
 * 3. Record the Z voltage (this should represent +1g)
 * 4. Flip sensor upside down (Z pointing down) 
 * 5. Record the Z voltage (this should represent -1g)
 * 6. Calculate: sensitivity = (voltage_up - voltage_down) / 2.0
 * 7. Calculate: zeroG = (voltage_up + voltage_down) / 2.0
 */

// Analog pins for accelerometer
const int xPin = A0;
const int yPin = A1;
const int zPin = A2;

float vcc = 5.0;

void setup() {
  Serial.begin(9600);
  Serial.println("=== ADXL335 Calibration Tool ===");
  Serial.println();
  Serial.println("Step 1: Place sensor FLAT on table (Z pointing UP)");
  Serial.println("Step 2: Record the voltages below");
  Serial.println("Step 3: Flip sensor UPSIDE DOWN (Z pointing DOWN)");
  Serial.println("Step 4: Record those voltages too");
  Serial.println();
  delay(3000);
}

void loop() {
  // Read raw values
  int xRaw = analogRead(xPin);
  int yRaw = analogRead(yPin);
  int zRaw = analogRead(zPin);
  
  // Convert to voltage
  float xVolt = (xRaw * vcc) / 1023.0;
  float yVolt = (yRaw * vcc) / 1023.0;
  float zVolt = (zRaw * vcc) / 1023.0;
  
  // Print raw voltages for calibration
  Serial.print("X: ");
  Serial.print(xVolt, 3);
  Serial.print("V   Y: ");
  Serial.print(yVolt, 3);
  Serial.print("V   Z: ");
  Serial.print(zVolt, 3);
  Serial.println("V");
  
  delay(1000);
}

/*
 * Calibration Process:
 * 
 * 1. FLAT POSITION (Z up): Record X, Y, Z voltages
 *    X_flat = ? V, Y_flat = ? V, Z_up = ? V
 * 
 * 2. FLIPPED POSITION (Z down): Record Z voltage
 *    Z_down = ? V
 * 
 * 3. Calculate calibration:
 *    zeroG = (Z_up + Z_down) / 2.0
 *    sensitivity = (Z_up - Z_down) / 2.0  [This represents 2g difference]
 * 
 * 4. For X and Y axes when flat, they should read close to zeroG
 * 
 * Example:
 * If Z_up = 2.2V and Z_down = 1.6V
 * Then zeroG = (2.2 + 1.6) / 2 = 1.9V
 * And sensitivity = (2.2 - 1.6) / 2 = 0.3V/g
 */
