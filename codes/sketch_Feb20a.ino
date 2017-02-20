#include <SoftwareSerial.h>  
SoftwareSerial BT(4, 9); // 接收, 传送，程序中2为RX需要接esp8266的TXD,9为TX，需要接esp8266的RX。

//Places to declare functions
void forwards(int forward_spped);
void backwards(int back_speed);
void leftwards(int left_speed);
void rightwards(int right_speed);
void stops();
void try_speed_cal();
void speed_cal();
int execution_time = 0;

// Constants to initialize wifi mode
int init_stage = 0;
char wifi_answer[8];
char oneline[32];
char convert_command[9];
char* wifi_command_set[] = {"AT\r\n",
                            "AT+CWMODE=3\r\n",
                            "AT+CWJAP=\"hobot_ad\",\"0123456789\"\r\n",
                            "AT+CIFSR\r\n",
                            "AT+CIPMUX=1\r\n",
                            "AT+CIPSERVER=0\r\n",
                            "AT+CIPSTART=1,\"TCP\",\"192.168.1.100\",5678\r\n",
                            "AT+CIPSEND=1,4\r\n",
                            "c3c\n"};
// if want to change baudrate, use command: "AT+UART=38400,8,1,0,0\r\n"

// Constants to detemine command: "c3+w255q\r\n"
char instruction_head = 'c';
int init_car_num = 3;
int received_car_num = 0;
char instruction_parity = 'q'; // quit
char command;
char speed_level_ch[3];
int speed_level = 0;
int speed_level_in_range = 0;
char tmp_ch; 
char* execution_stage[] = {"AT+CIPSEND=1,8\r\n",
                          "okok\n",
                          "nono\n"};

// speed track
unsigned int motor1=0;   //计左电机码盘脉冲值
unsigned int motor2=0;   //计右电机码盘脉冲值
unsigned int motor1_last=0;   //计左电机码盘脉冲值
unsigned int motor2_last=0;   //计右电机码盘脉冲值
float left_speed = 0.00;
float right_speed = 0.00;

//Super Simple Timer
const long aaEvery = 100;  // 100 milli seconds
unsigned long aaUp;  //  最後剛做過 speed_cal() 的時間
unsigned long bbUp;


// Pin Constants
const int EApin = 5; //motor driver enable: analong Write to control speed
const int EBpin = 6; //motor driver enable: analong Write to control speed
const int leftmotorpin1 = 7; // 直流电机信号输出
const int leftmotorpin2 = 8;
const byte rightmotorpin1 = 10;
const byte rightmotorpin2 = 11;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(38400); // 开始串行监测
  Serial.println("BT is ready!");
  // esp8266默认，115200, but arduino R3 only provide 57600bps at muximum
  // details: https://www.arduino.cc/en/Reference/SoftwareSerial
  BT.begin(38400);
  
  aaUp = millis( );  
 
  
  //信号输出接口
  for (int pinindex = 5; pinindex < 12; pinindex++) {
    pinMode(pinindex, OUTPUT); // set pins 5 to 11 as outputs
  }
  
  pinMode(3, INPUT_PULLUP);
  pinMode(2, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(2), left_motor, RISING);  
  attachInterrupt(digitalPinToInterrupt(3), right_motor,RISING);

  int wifi_init_success = wifi_init();
  Serial.println("Initialization success.");
}

void loop() {
  try_speed_cal(); 
  
  // read in 16 characters buffer
  for(int i=0; i<32; i++){
    if(BT.available()){
      oneline[i] = BT.read();
    }
  }


  // use the command format to convert the command, pack up the command into "convert_command"
  int j = 0;
  for(int i=0; i<32; i++){
    if(oneline[i] == 'c'){
      j = i;
      break;
    }
  }

  for(int i = 0; i<8; i++){
    convert_command[i] = oneline[j+i];
  }
  convert_command[8]=0;
  Serial.write("16 byte one line:");
  Serial.write(oneline);
  Serial.write("\n");
  Serial.write("command:");
  Serial.write(convert_command);
  Serial.write("\n");
  

  //
      //Serial.write("command is:");
      //Serial.write(convert_command);
      received_car_num = convert_command[1]-48;
      command = convert_command[3];
      speed_level = (convert_command[4]-48)*100 + (convert_command[5]-48)*10 + convert_command[6] -48;
      if (speed_level >= 0 && speed_level < 256){
          //Serial.print("speed_level:");
          //Serial.print(speed_level);
          //Serial.write("\n");
          speed_level_in_range = 1;
      }

  //Serial.print("left motor:");
  //Serial.print(motor1);
  //Serial.print("\tright motor:");
  //Serial.println(motor2);
  //Serial.print("left motor_last:");
  //Serial.print(motor1_last);
  //Serial.print("\tright motor_last:");
  //Serial.println(motor2_last);
    

  //Serial.println();
  //Serial.print(speed_level_in_range);

  // put your main code here, to run repeatedly:
  
      if( command == 'w' && speed_level_in_range == 1){
          BT.write(wifi_command_set[7]);
          forwards(speed_level);
          delay(50);
          command = 'q';
          speed_level = 0;
          BT.write("wok\n");
          clearBTbuffer();
          execution_time++;
          
          forwards(speed_level);
          delay(130);
      }
      else if( command == 's' && speed_level_in_range == 1){
          BT.write(wifi_command_set[7]);
          backwards(speed_level);
          delay(50);
          command = 'q';
          speed_level = 0;
          BT.write("sok\n");
          clearBTbuffer();
          execution_time++;

          backwards(speed_level);
          delay(130);
      }
      else if( command == 'a' && speed_level_in_range == 1){
          BT.write(wifi_command_set[7]);
          leftwards(speed_level);
          delay(50);
          command = 'q';
          speed_level = 0;
          BT.write("aok\n");
          clearBTbuffer();
          execution_time++;

          leftwards(speed_level-10);
          delay(30);
          leftwards(speed_level-10*2);
          delay(30);
          leftwards(speed_level-10*3);
          delay(30);
          leftwards(speed_level-10*4);
          delay(40);
      }
      else if( command == 'd' && speed_level_in_range == 1){
          BT.write(wifi_command_set[7]);
          rightwards(speed_level);
          delay(50);
          command = 'q';
          speed_level = 0;
          BT.write("dok\n");
          clearBTbuffer();
          execution_time++;

          rightwards(speed_level-10);
          delay(30);
          rightwards(speed_level-10*2);
          delay(30);
          rightwards(speed_level-10*3);
          delay(30);
          rightwards(speed_level-10*4);
          delay(40);
      }
      else{
          stops();
          //BT.write(wifi_command_set[7]);
          delay(10);
          //BT.write("non\n");
      }

      for(int i=0; i<32; i++){
          oneline[i] = 0;
      }
      Serial.print("executed time:");
      Serial.print(execution_time);
      Serial.print("\n");
}

//前进
void forwards(int forward_speed){
  //running = true;
  analogWrite(EApin, forward_speed);
  analogWrite(EBpin, forward_speed);
  digitalWrite(leftmotorpin1, HIGH);
  digitalWrite(leftmotorpin2, LOW);
  digitalWrite(rightmotorpin1, HIGH);
  digitalWrite(rightmotorpin2, LOW); 
  return ;
}

//后退
void backwards(int back_speed){
  //running = true;
  analogWrite(EApin, back_speed);
  analogWrite(EBpin, back_speed);
  digitalWrite(leftmotorpin1, LOW);
  digitalWrite(leftmotorpin2, HIGH);
  digitalWrite(rightmotorpin1, LOW);
  digitalWrite(rightmotorpin2, HIGH); 
  return ;
}

//左转
void leftwards(int left_speed){
   analogWrite(EApin, left_speed);
   analogWrite(EBpin, left_speed);
   digitalWrite(leftmotorpin1, HIGH);
   digitalWrite(leftmotorpin2, LOW);
   digitalWrite(rightmotorpin1, LOW);
   digitalWrite(rightmotorpin2, HIGH);
   return ;
}


//右转
void rightwards(int right_speed){
   analogWrite(EApin, right_speed);
   analogWrite(EBpin, right_speed);
   digitalWrite(leftmotorpin1, LOW);
   digitalWrite(leftmotorpin2, HIGH);
   digitalWrite(rightmotorpin1, HIGH);
   digitalWrite(rightmotorpin2, LOW);
   return ;
}

void stops(){
  //running = false;
  analogWrite(EApin, 0);
  analogWrite(EBpin, 0);
  digitalWrite(leftmotorpin1,HIGH);
  digitalWrite(leftmotorpin2, HIGH);
  digitalWrite(rightmotorpin1, HIGH);
  digitalWrite(rightmotorpin2, HIGH); 
  return ;
}

int wifi_init(){
  for (int i = 0; i < 8; i++){
      BT.write(wifi_command_set[i]);
      delay(3000);
      while(BT.available()){
      tmp_ch = BT.read();
      Serial.write(tmp_ch);
      }
   }
   
   BT.write(wifi_command_set[8]);
   for(int i=0; i<4; i++){
    wifi_answer[i] = BT.read();
   }
   if(wifi_answer[0] == 'C' && wifi_answer[1] == 'a' && wifi_answer[2] == 'r'&& wifi_answer[3] == '3'){
    init_stage = 1; // init success
   }
   return init_stage;
}

void left_motor()            //触发函数
{
  motor1++;  
  if(motor1>=999)
    motor1=0;
}

void right_motor()            //触发函数
{
  motor2++; 
  if(motor2>=999)
    motor2=0;
}

void try_speed_cal() {
  if(millis() - aaUp < aaEvery) return; // 時間還沒到
  speed_cal();  // 該吃藥囉 !
  aaUp = millis();
  
  //Serial.print("left_speed (round/s):");
  //Serial.print(left_speed);
  //Serial.print("\tright_speed (round/s):");
  //Serial.print(right_speed);
  //Serial.print("\n");
}

void speed_cal(){
  if(motor1 < motor1_last){
    left_speed = float(((motor1+1000)-motor1_last)/(0.001*millis()-0.001*aaUp)/20.00);
  }
  else{
    left_speed = float(((motor1)-motor1_last)/(0.001*millis()-0.001*aaUp)/20.00);
  }

  if(motor2 < motor2_last){
    right_speed = float(((motor2+1000)-motor2_last)/(0.001*millis()-0.001*aaUp)/20.00);
  }
  else{
    right_speed = float(((motor2)-motor2_last)/(0.001*millis()-0.001*aaUp)/20.00);
  }
  motor1_last = motor1;
  motor2_last = motor2;
  //Serial.print("aaUp:");
  //Serial.print(aaUp);
  //Serial.print("\t millis():");
  //Serial.print(millis());
  //Serial.print("\n");
  return;
}

void clearBTbuffer(){
  int cleanstop;
  Serial.print("Cleaning");
  Serial.print("\n");
  //delay(10);
  for(int i=0; i<80; i++){
    cleanstop = 0;
    if(BT.available()){
      tmp_ch = BT.read();
      if(tmp_ch == '+'){
          tmp_ch = BT.read();
          if(tmp_ch == 'I'){
            cleanstop++;
          }
          tmp_ch = BT.read();
          if(tmp_ch == 'P'){
            cleanstop++;
          }
          tmp_ch = BT.read();
          if(tmp_ch == 'D'){
            cleanstop++;
          }
          if(cleanstop == 3){
            break;
        }
      }
      else if(tmp_ch == 'S'){
        tmp_ch = BT.read();
          if(tmp_ch == 'E'){
            cleanstop++;
          }
          tmp_ch = BT.read();
          if(tmp_ch == 'N'){
            cleanstop++;
          }
          tmp_ch = BT.read();
          if(tmp_ch == 'D'){
            cleanstop++;
          }
          tmp_ch = BT.read();
          if(tmp_ch == ' '){
            cleanstop++;
          }
          tmp_ch = BT.read();
          if(tmp_ch == 'O'){
            cleanstop++;
          }
          tmp_ch = BT.read();
          if(tmp_ch == 'K'){
            cleanstop++;
          }
          if(cleanstop == 6){
            break;
          }
      }
      Serial.print(tmp_ch);
    }
  }
  return ;
}

