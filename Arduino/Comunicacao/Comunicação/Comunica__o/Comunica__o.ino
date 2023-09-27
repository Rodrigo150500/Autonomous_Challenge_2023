#include <Servo.h>

Servo servo;
#define pinServo 3

int ultimoAngulo = 90;
int Kp, Kd, Ki = 1;
int integral = 0;
int lastError = 0;

void setup() {
  // put your setup code here, to run once:
  servo.attach(pinServo);
  Serial.begin(9600);
  servo.write(90);
}

void loop() {
  servo.write(readSerial());
}

int readSerial(){
  if (Serial.available() > 0){
      int angulo = Serial.parseInt();
      if (angulo != 0){
        ultimoAngulo = angulo + 90;
        return ultimoAngulo;
      }else{
        return ultimoAngulo;
      }
 }
 }

 int controlPID(int setpoint, int inputValue) {
  // Calcule o erro (diferença entre o setpoint e o valor atual)
  int error = setpoint - inputValue;
  
  // Calcule o termo proporcional
  int P = Kp * error;
  
  // Calcule o termo integral
  integral += error;
  int I = Ki * integral;
  
  // Calcule o termo derivativo
  int derivative = error - lastError;
  int D = Kd * derivative;
  
  // Calcule a saída do controlador PID
  int output = P + I + D;
  
  // Limite a saída dentro dos limites do servo
  output = constrain(output, 0, 180);
  
  // Atualize o valor do erro anterior
  lastError = error;
  
  return output;
}
  
