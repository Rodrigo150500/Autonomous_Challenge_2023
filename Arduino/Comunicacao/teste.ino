#include <Servo.h>

Servo servo;
#define pinoServo 3
int ultimoAngulo = 0;

String readSerial(){
  String palavra = "";
  while(Serial.available()){
    char letra = Serial.read();
    if(letra != '\n'){
       palavra += letra;
    }else{
      return palavra;
    }
    
  }
}

int lerAngulo(){
  
  if (Serial.available() > 0){
    int numero = Serial.parseInt();
    if (numero != 0){
      numero = numero + 90;
      Serial.println(numero);
      return numero;
    }

  }
}

void setup() {
  // put your setup code here, to run once:
Serial.begin(9600);
servo.attach(pinoServo);
servo.write(90);
}

void loop() {
  // put your main code here, to run repeatedly:
 int angulo = lerAngulo();
 if (angulo != ultimoAngulo){
  servo.write(angulo);
 }

 ultimoAngulo = angulo;
 delay(100);
}
