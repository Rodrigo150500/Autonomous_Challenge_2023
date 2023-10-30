//CONFIGURAÇÃO DO SERVO
#include <Servo.h>
Servo servo;
#define pinServo 2
int ultimoAngulo = 90;
unsigned long tempoAng;
String direcao;


//CONFIGURAÇÃO DOS OBJETOS
//Variaveis para voltar a leitura dos objetos
unsigned long tempoPinVm;
unsigned long tempoPinAm;
unsigned long tempoPinVd;
unsigned long tempoPedestre;
unsigned long tempoPare;
unsigned long tempoPessoa;

//Variaveis para permitir a ação de parada
bool acessoPinVm = true;
bool acessoPinAm = true;
bool acessoPinVd = true;
bool acessoPedestre = true;
bool acessoPare = true;
bool acessoPessoa = true;

//Variaveis para armazenar os dados e quantidade de itens dentro da itensLista
String itensLista[50];
int indexItensLista;

//CONFIGURAÇÃO DOS MOTORES
//Setup dos motores
int TraseiraEsquerdaTras = 3; 
int TraseiraEsquerdaFrente = 4; 

int TraseiraDireitaTras = 5;
int TraseiraDireitaFrente = 6;

int FrenteEsquerdaTras = 7;
int FrenteEsquerdaFrente = 8;

int FrenteDireitaTras = 9;
int FrenteDireitaFrente = 10;




int pinLed = 13;

int motorSpeed = 50;

void setup() {
  // put your setup code here, to run once:
  //Iniciando os pinos dos motores
  //pinMode(FrenteDireita_RPWM_Output, OUTPUT);
  //pinMode(FrenteDireita_LPWM_Output, OUTPUT);
  pinMode(FrenteEsquerda_RPWM_Output, OUTPUT);
  pinMode(FrenteEsquerda_LPWM_Output, OUTPUT);
  pinMode(TraseiraDireita_RPWM_Output, OUTPUT);
  pinMode(TraseiraDireita_LPWM_Output, OUTPUT);
  pinMode(TraseiraEsquerda_RPWM_Output, OUTPUT);
  pinMode(TraseiraEsquerda_LPWM_Output, OUTPUT);

  pinMode(pinLed, OUTPUT);
  servo.attach(pinServo);
  Serial.begin(9600);
  servo.write(90);

  tempoAng = millis();
  tempoPinVm = millis();
  tempoPinAm = millis();
  tempoPinVd = millis();
  tempoPedestre = millis();
  tempoPare = millis();
  tempoPessoa = millis();
  pinMode(13, OUTPUT);
}

void loop(){
  analogWrite(9, 0); //TrasEsquerda
  analogWrite(10, 35);
  }


void AndaPraFrente(int motorSpeed) {
  // Carro anda para frente
  //analogWrite(FrenteDireita_RPWM_Output, motorSpeed); //TrasEsquerda
  //analogWrite(FrenteDireita_LPWM_Output, 0);

  analogWrite(FrenteEsquerda_RPWM_Output, motorSpeed); //TrasDireita
  analogWrite(FrenteEsquerda_LPWM_Output, 0);

  analogWrite(TraseiraDireita_RPWM_Output, motorSpeed); //FrenteEsquerda
  analogWrite(TraseiraDireita_LPWM_Output, 0);

  analogWrite(TraseiraEsquerda_RPWM_Output, motorSpeed); //FrenteDireita
  analogWrite(TraseiraEsquerda_LPWM_Output, 0);
}

void Stop() {
  // Pare todos os motores
  //analogWrite(FrenteDireita_RPWM_Output, 0);
  //analogWrite(FrenteDireita_LPWM_Output, 0);
  analogWrite(FrenteEsquerda_RPWM_Output, 0);
  analogWrite(FrenteEsquerda_LPWM_Output, 0);
  analogWrite(TraseiraDireita_RPWM_Output, 0);
  analogWrite(TraseiraDireita_LPWM_Output, 0);
  analogWrite(TraseiraEsquerda_RPWM_Output, 0);
  analogWrite(TraseiraEsquerda_LPWM_Output, 0);
}
 
//Aumenta a velocidade dos motores do lado direito em 50%
void Direita(int motorSpeed){
  //analogWrite(FrenteDireita_RPWM_Output, motorSpeed*1.5); //TrasEsquerda
  //analogWrite(FrenteDireita_LPWM_Output, 0);

  analogWrite(FrenteEsquerda_RPWM_Output, motorSpeed); //TrasDireita
  analogWrite(FrenteEsquerda_LPWM_Output, 0);

  analogWrite(TraseiraDireita_RPWM_Output, motorSpeed*1.5); //FrenteEsquerda
  analogWrite(TraseiraDireita_LPWM_Output, 0);

  analogWrite(TraseiraEsquerda_RPWM_Output, motorSpeed); //FrenteDireita
  analogWrite(TraseiraEsquerda_LPWM_Output, 0);
}

//Aumenta a velocidade dos motores do lado Esquedo em 50%
void Esquerda(int motorSpeed){
  //analogWrite(FrenteDireita_RPWM_Output, motorSpeed); //TrasEsquerda
  //analogWrite(FrenteDireita_LPWM_Output, 0);

  analogWrite(FrenteEsquerda_RPWM_Output, motorSpeed*1.5); //TrasDireita
  analogWrite(FrenteEsquerda_LPWM_Output, 0);

  analogWrite(TraseiraDireita_RPWM_Output, motorSpeed); //FrenteEsquerda
  analogWrite(TraseiraDireita_LPWM_Output, 0);

  analogWrite(TraseiraEsquerda_RPWM_Output, motorSpeed*1.5); //FrenteDireita
  analogWrite(TraseiraEsquerda_LPWM_Output, 0);
}
