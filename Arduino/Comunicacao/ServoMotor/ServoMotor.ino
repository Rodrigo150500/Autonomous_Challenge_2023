//CONFIGURAÇÃO DO SERVO
#include <Servo.h>
Servo servo;
#define pinServo 3
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
int FrenteDireita_RPWM_Output = 3; // Arduino PWM output pin 3; connect to IBT-2 pin 1 (RPWM)
int FrenteDireita_LPWM_Output = 4; // Arduino PWM output pin 4; connect to IBT-2 pin 2 (LPWM)
int FrenteEsquerda_RPWM_Output = 5; // Arduino PWM output pin 5; connect to IBT-2 pin 1 (RPWM)
int FrenteEsquerda_LPWM_Output = 6; // Arduino PWM output pin 6; connect to IBT-2 pin 2 (LPWM)
int TraseiraDireita_RPWM_Output = 7; // Arduino PWM output pin 7; connect to IBT-2 pin 1 (RPWM)
int TraseiraDireita_LPWM_Output = 8; // Arduino PWM output pin 8; connect to IBT-2 pin 2 (LPWM)
int TraseiraEsquerda_RPWM_Output = 9; // Arduino PWM output pin 9; connect to IBT-2 pin 1 (RPWM)
int TraseiraEsquerda_LPWM_Output = 10; // Arduino PWM output pin 10; connect to IBT-2 pin 2 (LPWM)

int pinLed = 13;

int motorSpeed = 35;

void setup() {
  // put your setup code here, to run once:
  //Iniciando os pinos dos motores
  pinMode(FrenteDireita_RPWM_Output, OUTPUT);
  pinMode(FrenteDireita_LPWM_Output, OUTPUT);
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

void loop() {
  //AndaPraFrente(motorSpeed);
    //AndaPraFrente(motorSpeed);
  // put your main code here, to run repeatedly:7

  //Leitura apenas se houver dados no serial
    if (Serial.available()>0){

    //Leitura a cada 20 milli
    if (millis() > tempoAng + 20){

      //Lendo e separando os dados do serial na variavel itensLista, sendo o 1°item o angulo e o resto os objetos
      // [[E15, 0, 1, 2,] E15 - 'E' Faz o diferencial da roda esquerda e o 15 o angulo do servo | Os outros 0, 1, 2, são os objeto sendo lido
      String comando = readSerial();
      separar(comando);

      //Armazenando qual a direção se é Meio, Esquerda ou Direita
      direcao = itensLista[0].substring(0,1);

      // Armazendo o tamanho de caracteres que tem o 1°item da itensLista para separar a direção do ângulo
      int indexAngDir = itensLista[0].length();
      int angulo = itensLista[0].substring(1, indexAngDir).toInt();

      //Controlando o servo e o diferencial
      servo.write(angle(angulo));
      if(direcao == "E"){
        Esquerda(motorSpeed);
      }else if (direcao == "D"){
        Direita(motorSpeed);
      }else if (direcao == "M"){
        AndaPraFrente(motorSpeed);
      }

      // Limpando a memoria da direção
      direcao = "";


      //Lendo os objetos e tomando uma ação para cada objeto
      //Sendo:
      // 0:Pedestre
      // 1: Farol Amarelo
      // 2: Farol Verde
      // 3: Farol Vermelho
      // 4: Pare
      // 5: Pessoa - Mas não estou tomando alguma ação 

       for (int i = 1; i <= indexItensLista-1; i++) {
        if(itensLista[i].toInt() == 0){ //Faixa de Pedestre
            //Liberando o acesso de parar o carro
            if(acessoPedestre == true){
              Stop();
              delay(5000);
              acessoPedestre = false;
              tempoPedestre = millis();
            }
            //Após 5 segundos o acesso fica bloqueado, tempo talvez suficiente do carro passar pelo objeto e não lê-lo novamente
            if(millis() > tempoPedestre + 5000){
              acessoPedestre = true;
              tempoPedestre = millis();
            }
        }else
       if(itensLista[i].toInt() == 1){//Farol Amarelo
          if(acessoPinAm == true){
              Stop();
              delay(5000);
              acessoPinAm = false;
              tempoPinAm = millis();
            }
            if(millis() > tempoPinAm + 5000){
              acessoPinAm = true;
              tempoPinAm = millis();
            }
        }else if(itensLista[i].toInt() == 2){//Farol Verde
          if(acessoPinVd == true){
              acessoPinVd = false;
              tempoPinVd = millis();
            }
            if(millis() > tempoPinVd + 5000){
              acessoPinVd = true;
              tempoPinVd = millis();
            }
        } else if(itensLista[i].toInt() == 3){//Farol Vermelho
          if(acessoPinVm == true){
              Stop();
              delay(5000);
              acessoPinVm = false;
              tempoPinVm = millis();
          }
          if(millis() > tempoPinVm + 5000){
              acessoPinVm = true;
              tempoPinVm = millis();
          }
        } else if(itensLista[i].toInt() == 4){ //Pare
          if(acessoPare == true){
              Stop();
              delay(5000);
              acessoPare = false;
              tempoPare = millis();
            }
            if(millis() > tempoPare + 5000){
              acessoPare = true;
            }
        }
        /*if(itensLista[i].toInt() == 5){ //Pessoa
          if(acessoPessoa == true){
              Stop();
              delay(5000);
              acessoPessoa = false;
              tempoPessoa = millis();
            }
            if(millis() > tempoPessoa + 5000){
              acessoPessoa = true;
            }
        }*/
       /*if(itensLista[i].toInt() == 5){ //Pessoa
          itensLista[50];
          indexItensLista = 0;

          while (acessoPessoa == true){
            Stop();


            delay(2000);
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
          acessoPessoa = true;
          String itensLista[50];
          indexItensLista = 0;

        }*/
        
      }

      //Limpando o vetor itensLista para o próximo loop entrar zerado e não entrar com os valores antigos
      String itensLista[50];
      //Variavel que contem a quantidade de itens da itensLista
      indexItensLista = 0;
      tempoAng = millis();
    }else{

      //Se não passar os 20 millis limpar a lista
      String itensLista[50];
      indexItensLista = 0;
    }


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

  }}

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
 
//Aumenta a velocidade dos motores do lado direito em 50%
void Direita(int motorSpeed){
  analogWrite(FrenteDireita_RPWM_Output, motorSpeed*1.5);
  analogWrite(FrenteDireita_LPWM_Output, 0);
  analogWrite(FrenteEsquerda_RPWM_Output, motorSpeed);
  analogWrite(FrenteEsquerda_LPWM_Output, 0);

  analogWrite(TraseiraDireita_RPWM_Output, motorSpeed*1.5);
  analogWrite(TraseiraDireita_LPWM_Output, 0);
  analogWrite(TraseiraEsquerda_RPWM_Output, motorSpeed);
  analogWrite(TraseiraEsquerda_LPWM_Output, 0);
}

//Aumenta a velocidade dos motores do lado Esquedo em 50%
void Esquerda(int motorSpeed){
  analogWrite(FrenteDireita_RPWM_Output, motorSpeed);
  analogWrite(FrenteDireita_LPWM_Output, 0);
  analogWrite(FrenteEsquerda_RPWM_Output, motorSpeed*1.5);
  analogWrite(FrenteEsquerda_LPWM_Output, 0);

  analogWrite(TraseiraDireita_RPWM_Output, motorSpeed);
  analogWrite(TraseiraDireita_LPWM_Output, 0);
  analogWrite(TraseiraEsquerda_RPWM_Output, motorSpeed*1.5);
  analogWrite(TraseiraEsquerda_LPWM_Output, 0);
}
