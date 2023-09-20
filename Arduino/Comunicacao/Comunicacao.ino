String letra = "nome";

void setup() {
  Serial.begin(9600); // Inicialize a comunicação serial
  pinMode(LED_BUILTIN, OUTPUT);

}

void loop() {
  char angulo = receberPycharm();
  Serial.println(angulo);
  if (angulo == 'G'){
    digitalWrite(LED_BUILTIN, HIGH);
    delay(250);
    digitalWrite(LED_BUILTIN, LOW);
    delay(250);
  }
} 

void enviarPycharm(String msg){
  Serial.print(msg);
}

char receberPycharm() {
  if (Serial.available() > 0) {
    // Se houver dados disponíveis na porta serial
    char data = Serial.read();  // Leia o próximo caractere
    Serial.print("Dado recebido: ");
    Serial.println(data);  // Imprima o dado recebido
      return data;

  }
}
