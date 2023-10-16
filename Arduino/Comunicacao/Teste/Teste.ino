#include <Servo.h>

//Declarando o servo
Servo servo;
#define pinServo 3

//Setup dos motores
int FrenteDireita_RPWM_Output = 3; // Arduino PWM output pin 3; connect to IBT-2 pin 1 (RPWM)
int FrenteDireita_LPWM_Output = 4; // Arduino PWM output pin 4; connect to IBT-2 pin 2 (LPWM)
int FrenteEsquerda_RPWM_Output = 5; // Arduino PWM output pin 5; connect to IBT-2 pin 1 (RPWM)
int FrenteEsquerda_LPWM_Output = 6; // Arduino PWM output pin 6; connect to IBT-2 pin 2 (LPWM)
int TraseiraDireita_RPWM_Output = 7; // Arduino PWM output pin 7; connect to IBT-2 pin 1 (RPWM)
int TraseiraDireita_LPWM_Output = 8; // Arduino PWM output pin 8; connect to IBT-2 pin 2 (LPWM)
int TraseiraEsquerda_RPWM_Output = 9; // Arduino PWM output pin 9; connect to IBT-2 pin 1 (RPWM)
int TraseiraEsquerda_LPWM_Output = 10; // Arduino PWM output pin 10; connect to IBT-2 pin 2 (LPWM)

//Velocidade dos motores
int motorSpeed = 43;

// Variaveis para o PID
int Kp, Kd, Ki = 1;
int integral = 0;
int lastError = 0;

//Variavel para iniciar o ultimo angulo;
int ultimoAngulo = 90;
int angulo;

//Lista de objetos

//Declarando o tempo millis()
unsigned long tempo;

String palavra;
String itensListas[50];
String objetos[50];
int indexItensListas = 0;
int indexK = 0;

bool n1, n3, n4 = false;

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
  
//
void setup() {
  // put your setup code here, to run once:
  servo.attach(pinServo);
  Serial.begin(9600);
  servo.write(90);

  //Iniciando os pinos dos motores
  pinMode(FrenteDireita_RPWM_Output, OUTPUT);
  pinMode(FrenteDireita_LPWM_Output, OUTPUT);
  pinMode(FrenteEsquerda_RPWM_Output, OUTPUT);
  pinMode(FrenteEsquerda_LPWM_Output, OUTPUT);
  pinMode(TraseiraDireita_RPWM_Output, OUTPUT);
  pinMode(TraseiraDireita_LPWM_Output, OUTPUT);
  pinMode(TraseiraEsquerda_RPWM_Output, OUTPUT);
  pinMode(TraseiraEsquerda_LPWM_Output, OUTPUT);

  pinMode(13, OUTPUT);
  delay(2000);  
  tempo = millis();
}




void loop() {
  if (millis() > tempo+20){
  if (Serial.available() > 0){
    AndaPraFrente(motorSpeed);
    //separar(readSerial());
    Serial.println(readSerial());
    angulo = itensListas[0].toInt();
    //Armazenando apenas a lista de objetos
    for (int k = 1; k<= indexItensListas+1;k++){
      objetos[indexK] = itensListas[k];
      indexK++;
    }

    //Movendo o servo
 

    //Condição para detecção de objetos
    for (int item = 0; item<=indexK; item++){

      if (objetos[item] == "1" && n1 == false ){
        Stop();
        delay(5000);
        n1 = true;
      }
      if(objetos[item] == "3" && n3 == false){
        Stop();
        delay(5000);
        n3 = true;
      }
      if(objetos[item] == "4" && n4 == false){

        Stop();
        delay(5000);
        n4 = true;
    }
    }
    indexK = 0;
    String itensListas[50];
    indexItensListas = 0;
    tempo = millis();
  }
  }
  

}

int readAngulo(){
  if (Serial.available() > 0){
      int angulo = Serial.parseInt();
      if (angulo != ultimoAngulo){
         if (angulo != 0){
          ultimoAngulo = angulo + 90;
          return ultimoAngulo;
        }else{
          return ultimoAngulo;
        }
      }

 }
 }

String readSerial(){
    String palavra = "";
    while (Serial.available() > 0){
      char c = Serial.read();
      palavra += c;
    }
    return palavra;
 }

void separar(String txt){
  int ultimoCaracter = txt.length()-2;

  if (txt[0] == '[' && txt[ultimoCaracter] == ']'){
    String itens = txt.substring(1,ultimoCaracter);

    String item;
    for (int i = 0; i<= itens.length()-1;i++){
        char c = itens[i];
        if (itens[i] == ','){
          itensListas[indexItensListas] = item;
          item = "";
          indexItensListas++;
        } else{
          item += itens[i];
        }       
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


