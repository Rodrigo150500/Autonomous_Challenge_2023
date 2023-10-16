#include <Servo.h>
Servo servo;
#define pinServo 3

#define pinVm 4
#define pinAm 5
#define pinVd 6
#define pedestre 7 //Branco
#define pessoa 8//Azul
#define pare 9
#define nada 10 // Branco

unsigned long tempoAng;
unsigned long tempoLed;
int leds[50] = {4,5,6,7,8,9,10};
int ultimoAngulo = 90;
String itensLista[50];
int indexItensLista;
String objetos[50];
void setup() {
  // put your setup code here, to run once:
  pinMode(pinVm, OUTPUT);
  pinMode(pinAm, OUTPUT);
  pinMode(pinVd, OUTPUT);
  pinMode(pedestre,OUTPUT);
  pinMode(pare, OUTPUT);

  servo.attach(pinServo);
  Serial.begin(9600);
  servo.write(90);
  tempoAng = millis();
  tempoLed = millis();
  pinMode(13, OUTPUT);
}

void loop() {

  // put your main code here, to run repeatedly:7
    if (Serial.available()>0){
    if (millis() > tempoAng + 50){
      //Lendo e separando os dados do serial
      String comando = readSerial();
      separar(comando);
      

      //Controlando o servo
      int angulo = itensLista[0].toInt();
      servo.write(angle(itensLista[0].toInt()));

      //Ação para fazer com a detecção de objetos
      //Arrumar a ordem dos leds para a ordem dos objetos
      for (int i = 1; i <= indexItensLista; i++) {
        if(itensLista[i].toInt() == i-1){
          digitalWrite(leds[i], HIGH);
          if (millis() > tempoLed + 250){
            digitalWrite(leds[i], LOW);
            tempoLed = millis();
          }

  
        }

      }
      
      String itensLista[50];
      indexItensLista = 0;
      tempoAng = millis();
    }
  }
  

  

}

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

  }}


String readSerial(){
    String palavra = "";
    while (Serial.available() > 0){
      char c = Serial.read();
      palavra += c;
    }
    palavra.trim();
    return palavra;
 }

