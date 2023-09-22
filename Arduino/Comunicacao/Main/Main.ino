#include <Servo.h>

Servo servo; // Crie um objeto Servo para controlar o servo motor
int servoAngle = 90; // Ângulo inicial do servo motor

int FrenteDireita_RPWM_Output = 3; // Arduino PWM output pin 3; connect to IBT-2 pin 1 (RPWM)
int FrenteDireita_LPWM_Output = 4; // Arduino PWM output pin 4; connect to IBT-2 pin 2 (LPWM)
int FrenteEsquerda_RPWM_Output = 5; // Arduino PWM output pin 5; connect to IBT-2 pin 1 (RPWM)
int FrenteEsquerda_LPWM_Output = 6; // Arduino PWM output pin 6; connect to IBT-2 pin 2 (LPWM)
int TraseiraDireita_RPWM_Output = 7; // Arduino PWM output pin 7; connect to IBT-2 pin 1 (RPWM)
int TraseiraDireita_LPWM_Output = 8; // Arduino PWM output pin 8; connect to IBT-2 pin 2 (LPWM)
int TraseiraEsquerda_RPWM_Output = 9; // Arduino PWM output pin 9; connect to IBT-2 pin 1 (RPWM)
int TraseiraEsquerda_LPWM_Output = 10; // Arduino PWM output pin 10; connect to IBT-2 pin 2 (LPWM)
int motorSpeed = 35;
int ultimoAngulo;

char lastCommand = '\0'; // Variável para armazenar o último comando processado usada nos comandos seriais
unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 50; // Ajuste este valor conforme necessário

void setup() {
  servo.attach(2); // Conecte o servo motor ao pino 2
  servo.write(servoAngle); // Defina o ângulo inicial do servo motor

  pinMode(FrenteDireita_RPWM_Output, OUTPUT);
  pinMode(FrenteDireita_LPWM_Output, OUTPUT);
  pinMode(FrenteEsquerda_RPWM_Output, OUTPUT);
  pinMode(FrenteEsquerda_LPWM_Output, OUTPUT);
  pinMode(TraseiraDireita_RPWM_Output, OUTPUT);
  pinMode(TraseiraDireita_LPWM_Output, OUTPUT);
  pinMode(TraseiraEsquerda_RPWM_Output, OUTPUT);
  pinMode(TraseiraEsquerda_LPWM_Output, OUTPUT);
  // Inicialize a comunicação serial
  Serial.begin(9600);
}

void AndaPraTras(int motorSpeed) {
  // Carro anda para trás (ré)
  analogWrite(FrenteDireita_RPWM_Output, 0);
  analogWrite(FrenteDireita_LPWM_Output, motorSpeed);
  analogWrite(FrenteEsquerda_RPWM_Output, 0);
  analogWrite(FrenteEsquerda_LPWM_Output, motorSpeed);
  analogWrite(TraseiraDireita_RPWM_Output, 0);
  analogWrite(TraseiraDireita_LPWM_Output, motorSpeed);
  analogWrite(TraseiraEsquerda_RPWM_Output, 0);
  analogWrite(TraseiraEsquerda_LPWM_Output, motorSpeed);
}

void AndaPraFrente(int motorSpeed) {
  // Carro anda para frente
  analogWrite(FrenteDireita_RPWM_Output, motorSpeed);
  analogWrite(FrenteDireita_LPWM_Output, 0);
  analogWrite(FrenteEsquerda_RPWM_Output, motorSpeed);
  analogWrite(FrenteEsquerda_LPWM_Output, 0);
  analogWrite(TraseiraDireita_RPWM_Output, motorSpeed);
  analogWrite(TraseiraDireita_LPWM_Output, 0);
  analogWrite(TraseiraEsquerda_RPWM_Output, motorSpeed);
  analogWrite(TraseiraEsquerda_LPWM_Output, 0);
}

void Stop() {
  // Pare todos os motores
  analogWrite(FrenteDireita_RPWM_Output, 0);
  analogWrite(FrenteDireita_LPWM_Output, 0);
  analogWrite(FrenteEsquerda_RPWM_Output, 0);
  analogWrite(FrenteEsquerda_LPWM_Output, 0);
  analogWrite(TraseiraDireita_RPWM_Output, 0);
  analogWrite(TraseiraDireita_LPWM_Output, 0);
  analogWrite(TraseiraEsquerda_RPWM_Output, 0);
  analogWrite(TraseiraEsquerda_LPWM_Output, 0);
}
int serialRead(){
  String data = "";
  while (Serial.available() != 0){
    char c = Serial.read();
    data+=c;
  }
  return data.toInt();
}
void loop() {
    AndaPraFrente(motorSpeed);
    int angulo = serialRead();

    if (angulo != ultimoAngulo){
      servo.write(angulo);

      ultimoAngulo = angulo;
    }
  }
  
