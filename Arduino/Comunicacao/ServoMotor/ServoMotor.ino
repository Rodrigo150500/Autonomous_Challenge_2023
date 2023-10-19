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

unsigned long tempoPinVm;
unsigned long tempoPinAm;
unsigned long tempoPinVd;
unsigned long tempoPedestre;
unsigned long tempoPare;
unsigned long tempoPessoa;

bool acessoPinVm = true;
bool acessoPinAm = true;
bool acessoPinVd = true;
bool acessoPedestre = true;
bool acessoPare = true;
bool acessoPessoa = true;



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
  pinMode(13, OUTPUT);
}

void loop() {
    //AndaPraFrente(motorSpeed);
  // put your main code here, to run repeatedly:7
    if (Serial.available()>0){
    if (millis() > tempoAng + 20){
      //Lendo e separando os dados do serial
      String comando = readSerial();
      separar(comando);
      //Controlando o servo
      servo.write(angle(itensLista[0].toInt()));

      //Ação para fazer com a detecção de objetos
      for (int i = 1; i <= indexItensLista-1; i++) {
        if(itensLista[i].toInt() == 0){ //Faixa de Pedestre
            if(acessoPedestre == true){
              digitalWrite(pedestre, HIGH);
              delay(1000);
              digitalWrite(pedestre,LOW);
              acessoPedestre = false;
              tempoPedestre = millis();
            }
            if(millis() > tempoPedestre + 5000){
              acessoPedestre = true;
              tempoPedestre = millis();
            }
        }
       if(itensLista[i].toInt() == 1){//Farol Amarelo
          if(acessoPinAm == true){
              digitalWrite(pinAm, HIGH);
              delay(1000);
              digitalWrite(pinAm,LOW);
              acessoPinAm = false;
              tempoPinAm = millis();
            }
            if(millis() > tempoPinAm + 5000){
              acessoPinAm = true;
              tempoPinAm = millis();
            }
        }
        if(itensLista[i].toInt() == 2){//Farol Verde
          if(acessoPinVd == true){
              digitalWrite(pinVd, HIGH);
              delay(1000);
              digitalWrite(pinVd,LOW);
              acessoPinVd = false;
              tempoPinVd = millis();
            }
            if(millis() > tempoPinVd + 5000){
              acessoPinVd = true;
              tempoPinVd = millis();
            }
        }
        if(itensLista[i].toInt() == 3){//Farol Vermelho
          if(acessoPinVm == true){
              digitalWrite(pinVm, HIGH);
              delay(1000);
              digitalWrite(pinVm,LOW);
              acessoPinVm = false;
              tempoPinVm = millis();
            }
            if(millis() > tempoPinVm + 5000){
              acessoPinVm = true;
              tempoPinVm = millis();
            }
        }
         if(itensLista[i].toInt() == 4){ //Pare
          if(acessoPare == true){
              digitalWrite(pare, HIGH);
              delay(1000);
              digitalWrite(pare,LOW);
              acessoPare = false;
              tempoPare = millis();
            }
            if(millis() > tempoPare + 5000){
              acessoPare = true;
              tempoPare = millis();
            }
        }
       /*if(itensLista[i].toInt() == 5){ //Pessoa
          itensLista[50];
          indexItensLista = 0;

          while (acessoPessoa == true){
            digitalWrite(pessoa, HIGH);
            delay(1000);
            String comam = readSerial();
            separar(comam);
            for (int m = 1; m <= indexItensLista-1; m++){
              if(itensLista[m].toInt() == 5){
                acessoPessoa = true;
                break;
              }else{
                if(m == indexItensLista-1 && acessoPessoa == true && itensLista[i] != 5){
                  acessoPessoa = false;
              }
              }
              
            } 
          itensLista[50];
          indexItensLista = 0;
          }
          digitalWrite(pessoa, LOW);
          acessoPessoa = true;
          String itensLista[50];
          indexItensLista = 0;

        }*/
        
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

 