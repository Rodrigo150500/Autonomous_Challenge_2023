//CONFIGURAÇÃO DO SERVO
#include <Servo.h>
#include <HCSR04.h>
Servo servo;
#define pinServo 2
int ultimoAngulo = 90;
unsigned long tempoAng;
String direcao;


//CONFIGURAÇÃO DOS OBJETOS
//Variaveis para voltar a leitura dos objetos
unsigned long tempoPinVm;
unsigned long tempoPare;

//Variaveis para permitir a ação de parada
bool acessoPinVm = true;
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

int FrenteDireitaTras = 10;
int FrenteDireitaFrente = 9;

int pinLed = 13;

int motorSpeed = 50;

//VARIAVEIS ULTRASSÔNICO
const int echoPin1 = 38;
const int trigPin1 = 36;

const int echoPin2 = 34;
const int trigPin2 = 32;

HCSR04 ultra1(echoPin1, trigPin1);
HCSR04 ultra2(echoPin2, trigPin2);


unsigned tempoUltra;



void setup() {
  // put your setup code here, to run once:
  //Iniciando os pinos dos motores
  pinMode(TraseiraEsquerdaTras, OUTPUT);
  pinMode(TraseiraEsquerdaFrente, OUTPUT);
  pinMode(TraseiraDireitaTras, OUTPUT);
  pinMode(TraseiraDireitaFrente, OUTPUT);
  pinMode(FrenteEsquerdaTras, OUTPUT);
  pinMode(FrenteEsquerdaFrente, OUTPUT);
  pinMode(FrenteDireitaTras, OUTPUT);
  pinMode(FrenteDireitaFrente, OUTPUT);

  pinMode(pinLed, OUTPUT);
  servo.attach(pinServo);
  Serial.begin(9600);
  servo.write(90);

  tempoAng = millis();
  tempoPinVm = millis();
  tempoPare = millis();
  tempoUltra = millis();
}
void loop() {

    /*if(ultra1.dist() > 0 && ultra1.dist() < 60){
      Stop();
      delay(500);
    }else{*/
    AndaPraFrente(motorSpeed);

    if (Serial.available() != 0) {
        if (millis() > tempoAng + 20) {
            String comando = readSerial();
            if(comando != '['){
              separar(comando);
            }
      

            direcao = itensLista[0].substring(0, 1);
            int indexAngDir = itensLista[0].length();
            int angulo = itensLista[0].substring(1, indexAngDir).toInt();
            servo.write(angle(angulo));


           if (direcao == "E") {
                Esquerda(motorSpeed,0.5,2.5);

            } else if (direcao == "D") {
                Direita(motorSpeed,0.5,2.5);

            }
            direcao = "";

            for (int i = 1; i <= indexItensLista - 1; i++) {
                   if (itensLista[i].toInt() == 3) {//Farol Vermelho
                   if (acessoPinVm == true) {
                        Stop();
                        delay(10000);
                        acessoPinVm = false;
                        tempoPinVm = millis();
                    }
                    if (millis() > tempoPinVm + 8000) {
                        acessoPinVm = true;
                    }
                } else if (itensLista[i].toInt() == 4) { //Pare 5s parado 5s para habilitar
                    if (acessoPare == true) {
                        Stop();
                        delay(5000);
                        acessoPare = false;
                        tempoPare = millis();
                    }
                    if (millis() > tempoPare + 8000) {
                        acessoPare = true;
                    }
                }else if (itensLista[i].toInt() == 5){//Pessoa
                  itensLista[50];
                  indexItensLista = 0;
                      while(acessoPessoa == true){
                        Stop();
                        delay(2000);

                        String coman = readSerial();
                        separar(coman);
                        for(int m = 1; m <= indexItensLista-1; m++){
                          if(itensLista[m] == 5){
                            acessoPessoa = true;
                            break;
                          }else if(m == indexItensLista-1 && acessoPessoa == true && itensLista[m] != 5){
                            acessoPessoa = false;
                          }
                        }
                      itensLista[50];
                      indexItensLista = 0;
                      }
                }
            }


            // Limpa o buffer da porta serial
            Serial.flush();

            // Limpa a matriz itensLista para o próximo loop
            indexItensLista = 0;
            tempoAng = millis();
        }
    //}

    }
}
//Função para mudar o angulo do servo tomando base os 90° como centro
int angle(int ang){
      if (ang+90 != ultimoAngulo){
         if (ang != 0){
          ultimoAngulo = ang + 90;
          return ultimoAngulo;
        }else{
          return ultimoAngulo;
        }
      }else{
        return ultimoAngulo;
      }
 }

//Separando os comandos entrado pelo serial
 void separar(String txt){
  int ultimoCaracter = txt.length()-1;
  if (txt[0] == '[' && txt[ultimoCaracter] == ']'){
    String itens = txt.substring(1,ultimoCaracter);
    String item;
    for (int i = 0; i<= itens.length();i++){
        char c = itens[i];
        if (itens[i] == ','){
          itensLista[indexItensLista] = item;
          item = "";
          indexItensLista++;
        } else{
          item += itens[i];
        }       
    }
  }
  
  }

//Lendo o serial
String readSerial(){
    String palavra = "";
    while (Serial.available() > 0){
      char c = Serial.read();
      palavra += c;
    }
    palavra.trim();
    return palavra;
 }

 //Movimentos dos motores
 void AndaPraFrente(int velocidade){
    analogWrite(TraseiraEsquerdaFrente, velocidade);
    analogWrite(TraseiraDireitaFrente, velocidade);
    analogWrite(FrenteDireitaFrente, velocidade);
    analogWrite(FrenteEsquerdaFrente, velocidade);


    analogWrite(FrenteDireitaTras, 0);
    analogWrite(TraseiraEsquerdaTras,0);
    analogWrite(TraseiraDireitaTras, 0);
    analogWrite(FrenteEsquerdaTras, 0);

 }

void Stop(){
    analogWrite(TraseiraEsquerdaFrente, 0);
    analogWrite(TraseiraDireitaFrente, 0);
    analogWrite(FrenteDireitaFrente, 0);
    analogWrite(FrenteEsquerdaFrente, 0);

    analogWrite(TraseiraEsquerdaTras,0);
    analogWrite(TraseiraDireitaTras, 0);
    analogWrite(FrenteDireitaTras, 0);
    analogWrite(FrenteEsquerdaTras, 0);
}

void Esquerda(int velocidade, int mInterno, int mExterno){
    analogWrite(TraseiraEsquerdaFrente, velocidade*mInterno);
    analogWrite(TraseiraDireitaFrente, velocidade*mExterno);
    analogWrite(FrenteDireitaFrente, velocidade*mExterno);
    analogWrite(FrenteEsquerdaFrente, velocidade*mInterno);


    analogWrite(FrenteDireitaTras, 0);
    analogWrite(TraseiraEsquerdaTras,0);
    analogWrite(TraseiraDireitaTras, 0);
    analogWrite(FrenteEsquerdaTras, 0);
}

void Direita(int velocidade, int mInterno, int mExterno){
    analogWrite(TraseiraEsquerdaFrente, velocidade*mExterno);
    analogWrite(TraseiraDireitaFrente, velocidade*mInterno);
    analogWrite(FrenteDireitaFrente, velocidade*mInterno);
    analogWrite(FrenteEsquerdaFrente, velocidade*mExterno);


    analogWrite(FrenteDireitaTras, 0);
    analogWrite(TraseiraEsquerdaTras,0);
    analogWrite(TraseiraDireitaTras, 0);
    analogWrite(FrenteEsquerdaTras, 0);
}