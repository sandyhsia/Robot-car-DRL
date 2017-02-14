#define DEBUG 0    // set to 1 to print to serial monitor, 0 to disable

#include <SoftwareSerial.h>  
SoftwareSerial BT(2, 9); // 接收, 传送，程序中2为RX需要接esp8266的TXD,9为TX，需要接esp8266的RX。

//Places to declare functions
void forwards(int forward_spped);
void backwards(int back_speed);
void leftwards(int left_speed);
void rightwards(int right_speed);
void stops();

// Constants to initialize wifi mode
int init_stage = 0;
char wifi_answer[8];
char oneline[20];
char convert_command[9];
char* wifi_command_set[] = {"AT\r\n",
                            "AT+CWMODE=3\r\n",
                            "AT+CWJAP=\"hobot_ad\",\"0123456789\"\r\n",
                            "AT+CIFSR\r\n",
                            "AT+CIPMUX=1\r\n",
                            "AT+CIPSERVER=0\r\n",
                            "AT+CIPSTART=1,\"TCP\",\"192.168.1.100\",8080\r\n",
                            "AT+CIPSEND=1,4\r\n",
                            "Car3"};
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

// Pin Constants
const int EApin = 3; //motor driver enable: analong Write to control speed
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
 
  
  //信号输出接口
  for (int pinindex = 6; pinindex < 12; pinindex++) {
    pinMode(pinindex, OUTPUT); // set pins 6 to 11 as outputs
  }
  pinMode(EApin, OUTPUT); // set pins 7 to 11 as outputs

  int wifi_init_success = wifi_init();
  Serial.println("Initialization success.");
}

void loop() {
  
  // read in 20 characters buffer
  for(int i=0; i<20; i++){
    if(BT.available()){
      oneline[i] = BT.read();
    }
  }


  // use the command format to convert the command, pack up the command into "convert_command"
  int j = 0;
  for(int i=0; i<20; i++){
    if(oneline[i] == 'c'){
      j = i;
      break;
    }
  }

  for(int i = 0; i<8; i++){
    convert_command[i] = oneline[j+i];
  }
  convert_command[8]=0;
  Serial.write("command:");
  Serial.write(convert_command);
  Serial.write("\n");
  

  //
  if(convert_command[7] == 'q'){
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
  }
    

  //Serial.println();
  //Serial.print(speed_level_in_range);

  // put your main code here, to run repeatedly:
  
      if( command == 'w' && speed_level_in_range == 1){
          forwards(speed_level);
          delay(30);
          command = 'q';
          speed_level = 0;
      }
      else if( command == 's' && speed_level_in_range == 1){
          backwards(speed_level);
          delay(30);
          command = 'q';
          speed_level = 0;
      }
      else if( command == 'a' && speed_level_in_range == 1){
          leftwards(speed_level);
          delay(30);
          command = 'q';
          speed_level = 0;
      }
      else if( command == 'd' && speed_level_in_range == 1){
          rightwards(speed_level);
          delay(30);
          command = 'q';
          speed_level = 0;
      }
      else{
          stops();
      }
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
      delay(2000);
      while(BT.available()){
      tmp_ch = BT.read();
      Serial.write(tmp_ch);
      }
   }
   
   BT.write(wifi_command_set[9]);
   for(int i=0; i<4; i++){
    wifi_answer[i] = BT.read();
   }
   if(wifi_answer[0] == 'C' && wifi_answer[1] == 'a' && wifi_answer[2] == 'r'&& wifi_answer[3] == '3'){
    init_stage = 1; // init success
   }
   return init_stage;
}

