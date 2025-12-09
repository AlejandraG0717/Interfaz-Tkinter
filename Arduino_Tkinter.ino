#include "Freenove_WS2812_Lib_for_ESP32.h"
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL343.h>
#include "SparkFun_CAP1203.h" 
#include <Wire.h>

#define pinLEDR1_L 3 //D1
#define pinLEDR2_L 46 //D2
#define pinLEDG_H 45 //D3

#define LEDS_COUNT  1
#define LEDS_PIN	41
#define CHANNEL		0

#define Vo_LUZ 4   // Pin asociado a ILUM
#define NTCp 5     // Pin asociado a NTC en el puente (extremo positivo)
#define NTCn 6     // Pin asociado a la referencia en el puente (extremo negativo)

#define CS_ACCELEROMETER 2
#define SCK_PIN 40
#define MISO_PIN 38
#define MOSI_PIN 39

Freenove_ESP32_WS2812 strip = Freenove_ESP32_WS2812(LEDS_COUNT, LEDS_PIN, CHANNEL);

Adafruit_ADXL343 accel = Adafruit_ADXL343(CS_ACCELEROMETER, &SPI);

CAP1203 sensor; 

int16_t  LUZ_meas;
float LUZ_uA;
int16_t  valorNTCp;
int16_t  valorNTCn;
int16_t  diferNTC;
float accel_x, accel_y, accel_z;
bool CAP_izq = false, CAP_cen = false, CAP_der = false;

void setup() {

  Serial.begin(115200);
  pinMode(pinLEDR1_L, OUTPUT);
  pinMode(pinLEDR2_L, OUTPUT);
  pinMode(pinLEDG_H, OUTPUT);
  digitalWrite(pinLEDR1_L, HIGH);
  digitalWrite(pinLEDR2_L, HIGH);
  digitalWrite(pinLEDG_H, LOW);
  strip.begin();
  strip.setBrightness(100);
  strip.show();
  pinMode(Vo_LUZ, ANALOG);  // Configurar pin asociado ILUM
  pinMode(NTCp, ANALOG);    // Configurar pines asociados a NTC
  pinMode(NTCn, ANALOG);
  delay(1000); 

  Wire.begin(12,13); 

  // Inicializar SPI
  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN, CS_ACCELEROMETER);

  // Inicializar acelerómetro
  if (!accel.begin()) {
    Serial.println("No se detectó el ADXL343.");
    while (1);
  }
  accel.setRange(ADXL343_RANGE_2_G);
  Serial.println("ADXL343 conectado.");

    // Setup sensor
  if (sensor.begin() == false)
  {
    Serial.println("Not connected. Please check connections and read the hookup guide.");
    while (1)
      ;
  }
  else
  {
    Serial.println("Connected!");
  }

}

void loop() {

  //ILUM
  LUZ_meas = analogRead(Vo_LUZ);
  LUZ_uA = 1000*(LUZ_meas/4096.0)*3.3/6.8;
  //Temperatura
  valorNTCp = analogRead(NTCp);
  valorNTCn = analogRead(NTCn);
  diferNTC = valorNTCp-valorNTCn;

  sensors_event_t event;
  accel.getEvent(&event);
  accel_x = event.acceleration.x;
  accel_y = event.acceleration.y;
  accel_z = event.acceleration.z;


  CAP_izq= sensor.isLeftTouched();
  CAP_cen = sensor.isMiddleTouched();
  CAP_der = sensor.isRightTouched();


  String mensaje = "ILUM: " + String(LUZ_uA) + " uA, NTC: " + String(diferNTC) + "  AccelerometroX: " + String(accel_x) + "  AccelerometroY: " + String(accel_y) + "  AccelerometroZ: " + String(accel_z) + " izquierda: " + String(CAP_izq) + " centro: " + String(CAP_cen) + " derecha: " + String(CAP_der);
  Serial.println(mensaje);
  delay(1000);

  if (Serial.available() > 0){
    String cmd = Serial.readString();
    cmd.trim();

    if (cmd=="D1"){
      toggleLED(pinLEDR1_L);
    }
    if (cmd=="D2"){
      toggleLED(pinLEDR2_L);
    }
    if (cmd=="D3"){
      toggleLED(pinLEDG_H);
    }
    if (cmd.startsWith("RGB(") && cmd.endsWith(")")) {
      int r, g, b;
      sscanf(cmd.c_str(), "RGB(%d,%d,%d)", &r, &g, &b);
      strip.setLedColor(0, r, g, b);
      strip.show();
    }
  }
}

void toggleLED(int pin) {
  digitalWrite(pin, !digitalRead(pin));
}
