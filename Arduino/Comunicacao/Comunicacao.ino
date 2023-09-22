
void setup() {
  Serial.begin(9600);
}
String palavra = "";
int angulo = 0;
void loop() {
  palavra = readSerial();
  //angulo = stringToInt(palavra);
  Serial.println(palavra);
  delay(50);
}

String readSerial(){
  String palavra = "";
  while (Serial.available() > 0){
    char c = Serial.read();
    palavra += c;
  }
  return palavra;
}


int stringToInt(String str) {
  return str.toInt();
}
