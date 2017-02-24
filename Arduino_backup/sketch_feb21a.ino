char t[4];

void setup() {
  t[0] = 'a';
  t[1] = 0;
  t[2] = 'd';
  t[3] = 'h';
  Serial.begin(9600);
}

void loop() {
  Serial.print(t);
  Serial.print("\n");

}
