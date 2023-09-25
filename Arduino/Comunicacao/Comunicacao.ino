#include <Servo.h>
Servo servo;
int pos;
#define SERVO 3
int angulo;
void setup() {
  Serial.begin(115200);
  servo.attach(SERVO);
  servo.write(0);
}
String palavra = "";
void loop() {
  palavra = readSerial();
  angulo = stringToInt(palavra);
  servo.write(90);
  delay(50);
}

int readSerial(){
  String palavra = "";
  int angulo = 0;
  while (Serial.available() > 0){
    char c = Serial.read();
    palavra += c;
  }
  angulo = palavra.toInt();
  return angulo;
}


int stringToInt(String str) {
  return str.toInt();
}
