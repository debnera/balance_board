/*
  Arduino LSM9DS1 - Gyroscope Application

  Based on public domain LSM9DS1 library example files.

  The circuit:
  - Arduino Nano 33 BLE

  Modified to send gyroscope data over BLE.
*/

#include <Arduino_LSM9DS1.h>
#include <ArduinoBLE.h>

 // Bluetooth® Low Energy Battery Service
BLEService orientationService("19B10000-E8F2-537E-4F6C-D104768A1214");
BLEStringCharacteristic orientationCharacteristic("19B10001-E8F2-537E-4F6C-D104768A1214", BLERead | BLEWrite | BLENotify, 15);
BLEByteCharacteristic pitchCharacteristic("19B10001-E8F2-537E-4F6C-D104768A1215", BLERead | BLEWrite | BLENotify);
BLEByteCharacteristic rollCharacteristic("19B10001-E8F2-537E-4F6C-D104768A1216", BLERead | BLEWrite | BLENotify);

float x, y, z;
float ac_x, ac_y, ac_z;
float gy_x, gy_y, gy_z;
float mag_x, mag_y, mag_z, mag_yaw;
float ac_pitch, ac_roll, ac_yaw;
float gy_pitch, gy_roll, gy_yaw;
float pitch, roll, yaw;
float alpha;


float dt;

unsigned long prev_time;


void send_orientation() {
    orientationCharacteristic.writeValue(String(yaw) + "," + String(pitch) + "," + String(roll));

    // Send in bytes to minimize data transmitted
    unsigned char pitch_byte = constrain(pitch + 128, 0, 255);
    pitchCharacteristic.writeValue(pitch_byte);
    unsigned char roll_byte = constrain(roll + 128, 0, 255);
    rollCharacteristic.writeValue(roll_byte);
}

void calibrate() {
  if (IMU.accelerationAvailable()) {
    Serial.println("Calibrating in 0.1 seconds");
    delay(100);
    IMU.readAcceleration(ac_x, ac_y, ac_z);

    pitch = atan2(ac_x, sqrt(pow(ac_y, 2) + pow(ac_z, 2))) * RAD_TO_DEG;
    roll = atan2(ac_y, sqrt(pow(ac_x, 2) + pow(ac_z, 2))) * RAD_TO_DEG;
    Serial.println("Initial position is: " + String(yaw) + ", " + String(pitch) + ", " + String(roll));
    yaw = 0;
    gy_pitch = 0;
    gy_roll = 0;
    gy_yaw = 0;
  }
}


void setup() {
  Serial.begin(9600);
  delay(100);
  Serial.println("Started");

  

  // Setup IMU
  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }
  Serial.print("Gyroscope sample rate = ");
  Serial.print(IMU.gyroscopeSampleRate());
  Serial.println(" Hz");
  Serial.println();
  Serial.println("Gyroscope in degrees/second");

  calibrate();
  prev_time = millis();

  
  // Setup bluetooth
  Serial.println("Setting up bluetooth...");
  if (!BLE.begin()) {
    Serial.println("starting Bluetooth® Low Energy module failed!");
    while (1);
  }
  BLE.setLocalName("BalanceBoardController");
  BLE.setAdvertisedService(orientationService); // add the service UUID
  orientationService.addCharacteristic(orientationCharacteristic); // add the orientation characteristic
  orientationService.addCharacteristic(pitchCharacteristic); // add the orientation characteristic
  orientationService.addCharacteristic(rollCharacteristic); // add the orientation characteristic
  BLE.addService(orientationService); // Add the orientation service
  send_orientation();  // Set initial value for bluetooth characteristic
  BLE.setConnectionInterval(0x0006, 0x0006);
  BLE.advertise();
  Serial.println("Bluetooth up!");

}


void loop() {
  
  BLEDevice central = BLE.central();

  if (central.connected()) {
    // Calibrate when a connection is established
    Serial.println("Connection found - calibrating...");
    calibrate();
  }

  // Keep sending measurements while the connection is up
  while (central.connected()) {
    


    bool orientation_updated = false;

    while (IMU.accelerationAvailable()) {
      IMU.readAcceleration(ac_x, ac_y, ac_z);
      //Serial.println(String(x) + ", " + String(y) + ", " + String(z));

      ac_pitch = atan2(ac_x, sqrt(pow(ac_y, 2) + pow(ac_z, 2))) * RAD_TO_DEG;
      ac_roll = -atan2(ac_y, sqrt(pow(ac_x, 2) + pow(ac_z, 2))) * RAD_TO_DEG;  // negative to match perceived orientation of the nano 33 board
      //delay(100);
    }
    while (IMU.gyroscopeAvailable()) {

      IMU.readGyroscope(gy_x, gy_y, gy_z);
      //dt = (millis() - prev_time) / 1000;  // deltatime in seconds
      dt = 1.0 / 104; // 104 Hz is the default output rate
      gy_pitch = gy_pitch + gy_y * dt;  // gy_y seems to correlate with accel roll
      gy_roll = gy_roll + gy_x * dt;  // gy_x seems to correlate with accel pitch
      gy_yaw = gy_yaw + gy_z * dt;
      alpha = 0.9;
      pitch = alpha * (pitch + gy_y * dt) + (1-alpha) * ac_pitch;
      roll = alpha * (roll + gy_x * dt) + (1-alpha) * ac_roll;
      yaw = gy_yaw;
      //Serial.println(String(x) + ", " + String(y) + ", " + String(z));

      prev_time = millis();
      //delay(100);
      orientation_updated = true;
    }

    while (IMU.magneticFieldAvailable()) {
      IMU.readMagneticField(y, x, z);

      mag_x = x*cos(pitch * DEG_TO_RAD)+y*sin(roll * DEG_TO_RAD)*sin(pitch * DEG_TO_RAD) + z*sin(pitch * DEG_TO_RAD)*cos(roll * DEG_TO_RAD);

      mag_y = -y*cos(roll * DEG_TO_RAD) + z*sin(roll * DEG_TO_RAD);

      mag_yaw =  atan2(-mag_y,mag_x) * RAD_TO_DEG;
      //Serial.println(mag_yaw);
    }

    if (orientation_updated) {
      // Only send the new orientation, if we have perceived new information
      send_orientation();
      Serial.println(String(yaw) + ", " + String(pitch) + ", " + String(roll));
    }
    delay(1);  // Save computation power by sleeping for 1ms (update rate is around 10 ms or 104 Hz)

  //Serial.println(String(yaw) + ", " + String(pitch) + ", " + String(roll));
  //Serial.println(String(gy_yaw) + ", " + String(gy_pitch) + ", " + String(gy_roll));
  //Serial.println(String(dt) + ", " + String(gy_pitch) + ", " + String(gy_x));
  //Serial.println(String(yaw) + ", " + String(ac_pitch) + ", " + String(ac_roll));
  /*
  Serial.print("yaw: (" + String(yaw) + ", " + String(gy_yaw) + ")");
  Serial.print(", ");
  Serial.print("pitch: (" + String(gy_pitch) + ", " + String(ac_pitch) + ")");
  Serial.print(", ");
  Serial.print("roll: (" + String(gy_roll) + ", " + String(ac_roll) + ")");
  Serial.println();
  */
  }

}