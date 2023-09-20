void setup() {
  Serial.begin(115200); // Inicialize a comunicação serial
  pinMode(13, OUTPUT);
}

void loop() {
String data = receberPycharm();
if (data){
  
}
Serial.print(data);

} 

void enviarPycharm(String msg){
  Serial.print(msg);
}

String receberPycharm() {
  String data = "";
  
  while (Serial.available() != 0) {
    // Se houver dados disponíveis na porta serial
    char letra = Serial.read();  // Leia o próximo caractere
    data += letra;
  }
  return data;


}
