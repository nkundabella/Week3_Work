#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

void setup() {
  Serial.begin(115200);  // match Processing serial speed
  Wire.begin();
  mpu.initialize();

  if (!mpu.testConnection()) {
    Serial.println("MPU6050 connection failed!");
    while (1);
  }
  Serial.println("MPU6050 ready!");
}

void loop() {
  int16_t ax, ay, az;
  int16_t gx, gy, gz;

  // Read raw accelerometer and gyroscope values
  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

  // Convert accelerometer data to pitch and roll (in degrees)
  float pitch = atan2(ax, sqrt(ay*ay + az*az)) * 180.0 / PI;
  float roll  = atan2(ay, sqrt(ax*ax + az*az)) * 180.0 / PI;

  // Send pitch and roll to Processing
  Serial.print(pitch);
  Serial.print(",");
  Serial.println(roll);

  delay(50); // 20Hz update rate
}