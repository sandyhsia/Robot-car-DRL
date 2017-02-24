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
int check_recover();
void backup();
void use_backup();
int execution_time = 0;
int proc_stage = 0;

// Constants to initialize wifi mode
int init_stage = 0;
char wifi_answer[8];
char oneline[32];
char convert_command[9];
char backup_command[9];
char* wifi_command_set[] = {"AT\r\n",
                            "AT+CWMODE=3\r\n",
                            "AT+CWJAP=\"Hobot_AutonomouDriving\",\"czs918170\"\r\n",
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
const long aaEvery = 100;  // 100 milli seconds for speed cal
unsigned long aaUp;  //  最後剛做過 speed_cal() 的時間
const long income_Every = 500;  // 500 milli seconds
unsigned long incomeUp;


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
  incomeUp = 0;
  
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
  
  
  
  // read in 24 characters buffer
  for(int i=0; i<24; i++){
    if(BT.available()){
      oneline[i] = BT.read();
      //if(oneline[i]==0){
      //  break;
      //}
      if(oneline[i] == 'c'){
        for(int j = 0; j < 7; j++){
          oneline[i+j+1] = BT.read();
        }
        break;
      }
    }
  }
  proc_stage = 1;


  // use the command format to convert the command, pack up the command into "convert_command"
  int j = -1;
  for(int i=0; i<32; i++){
    if(oneline[i] == 'c'){                // first find 'c' and try convert line --> command
      j = i;
      break;
    }
  }
  if(j >= 0){
    proc_stage = 2;
    for(int i = 0; i<8; i++){
      convert_command[i] = oneline[j+i];
    }
  }
  
  if(proc_stage == 1){                    // if not find 'c', then find ':' and try convert line --> command
    j = -1;
    for(int i=0; i<32; i++){
      if(oneline[i] == ':'){
        j = i;
        break;
      }
    }
    if(j >= 0){
      proc_stage = 2;
      for(int i = 0; i<8; i++){
        convert_command[i] = oneline[j+i+1];
      }
    }
  }

  if(proc_stage == 1){                    // if still not find ':', then find '+' and try convert line --> command
    j = -1;
    for(int i=0; i<32; i++){
      if(oneline[i] == '+'){
        j = i;
        break;
      }
    }
    if(j >= 0){
      proc_stage = 2;
      if(j >= 2){
        for(int i = 0; i<8; i++){
          convert_command[i] = oneline[j-2+i];
        }
      }
      else{
        for(int i = 0; i<8; i++){
          convert_command[i] = oneline[i];
        }
      }
    }
  }

  if(proc_stage == 1){                    // if still not find '+', then find 'w'(direction_ch) and try convert line --> command
    j = -1;
    for(int i=0; i<32; i++){
      if(oneline[i] == 'w' or oneline[i] == 'a' or oneline[i] == 's' or oneline[i] == 'd'){
        j = i;
        break;
      }
    }
    if(j >= 0){
      proc_stage = 2;
      if(j >= 3){
        for(int i = 0; i<8; i++){
          convert_command[i] = oneline[j-3+i];
        }
      }
      else{
        for(int i = 0; i<8; i++){
          convert_command[i] = oneline[i];
        }
      }
    }
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
      else if(convert_command[0] == 'c' or (convert_command[0]>47 and convert_command[0]<58) or convert_command[0] == '+' or convert_command[0] == 'w' or convert_command[0] == 'a' or convert_command[0] == 's' or convert_command[0] == 'd' or convert_command[0] == 'q'){
        if(speed_level_in_range == 0 and (command!= 'w' or command!='a' or command!='s' or command!='d' or command!='q')){
          check_recover();
          received_car_num = convert_command[1]-48;
          command = convert_command[3];
          speed_level = (convert_command[4]-48)*100 + (convert_command[5]-48)*10 + convert_command[6] -48;
        }
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
          BT.write("wok\n");
          clearBTbuffer();
          execution_time++;
          
          forwards(speed_level);
          delay(130);
          command = 'q';
          speed_level = 0;
          speed_level_in_range = 0;
          backup();
          incomeUp = millis();
      }
      else if( command == 's' && speed_level_in_range == 1){
          BT.write(wifi_command_set[7]);
          backwards(speed_level);
          delay(50);
          BT.write("sok\n");
          clearBTbuffer();
          execution_time++;

          backwards(speed_level);
          delay(130);
          command = 'q';
          speed_level = 0;
          speed_level_in_range = 0;
          backup();
          incomeUp = millis();
      }
      else if( command == 'a' && speed_level_in_range == 1){
          BT.write(wifi_command_set[7]);
          leftwards(speed_level);
          delay(50);
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

          command = 'q';
          speed_level = 0;
          speed_level_in_range = 0;
          backup();
          incomeUp = millis();
      }
      else if( command == 'd' && speed_level_in_range == 1){
          BT.write(wifi_command_set[7]);
          rightwards(speed_level);
          delay(50);
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
          
          command = 'q';
          speed_level = 0;
          speed_level_in_range = 0;
          backup();
          incomeUp = millis();
      }
      else if( command == 'q' && speed_level_in_range == 1){
          BT.write(wifi_command_set[7]);
          stops();
          delay(50);
          BT.write("qok\n");
          clearBTbuffer();
          execution_time++;

          delay(130);
          command = 'q';
          speed_level = 0;
          speed_level_in_range = 0;
          backup();
          incomeUp = millis();
      }
      else{
          stops();
          //BT.write(wifi_command_set[7]);
          delay(10);
          //BT.write("non\n");
          try_ask_server();
      }

      for(int i=0; i<32; i++){
          oneline[i] = 0;
      }
      for(int i=0; i<9; i++){
          convert_command[i] = 0;
      }
      Serial.print("executed time:");
      Serial.print(execution_time);
      Serial.print("\n");
      proc_stage = 0;
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
      if(tmp_ch == ':'){
        break;
      }
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
      else if(tmp_ch == 'C'){
        tmp_ch = BT.read();
          if(tmp_ch == 'L'){
            cleanstop++;
          }
          tmp_ch = BT.read();
          if(tmp_ch == 'O'){
            cleanstop++;
          }
          tmp_ch = BT.read();
          if(tmp_ch == 'S'){
            cleanstop++;
          }
          tmp_ch = BT.read();
          if(tmp_ch == 'D'){
            cleanstop++;
          }
           if(cleanstop == 4){
            reConnect();
           }
      }
      Serial.print(tmp_ch);
    }
  }
  return ;
}

int check_recover(){
  
  int get_start_ch = 0;
  int get_end_ch = 0;
  int get_speed_level = 0;
  int get_car_num = 0;
  int get_direction = 0;
  int get_separation = 0;
  int similarity = 0;
  char restore_command[9];
  int restore_finished = 0;

  int i = 0;
  while(i < 8){
    if(convert_command[i] == 'c'){
      get_start_ch = 1;
      restore_command[0]= 'c';
      break;
    }
    i++;
  }
  if(i>=0 and i < 8){
    if(convert_command[i+1]>47 and convert_command[i+1]<58){
      get_car_num = 1;
      restore_command[1]= convert_command[i+1];
    }
  }

   i = 0;
   while(i < 8){
    if(convert_command[i] == 'q'){
      get_end_ch = 1;
      restore_command[7]='q';
      break;
    }
    i++;
  }

   i = 0;
   while(i < 8){
    if(convert_command[i] == '+'){
      get_separation = 1;
      restore_command[2]='+';
      break;
    }
    i++;
  }
  if(i>0 and get_car_num == 0){
    if(convert_command[i-1]>47 and convert_command[i-1]<58){
      get_car_num = 1;
      restore_command[1]= convert_command[i-1];
    }
  }

   i = 0;
   while(i < 8){
    if(convert_command[i] == 'w' or convert_command[i] == 's' or convert_command[i] == 'a' or convert_command[i] == 'd' or convert_command[i] == 'q'){
      get_direction = 1;
      restore_command[3]= convert_command[i];
      break;
    }
    i++;
  }

  if(convert_command[i+1]>47 and convert_command[i+1]<58 and convert_command[i+2]>47 and convert_command[i+2]<58 and convert_command[i+3]>47 and convert_command[i+3]<58){
    get_speed_level = 1;
    restore_command[4]= convert_command[i+1];
    restore_command[5]= convert_command[i+2];
    restore_command[6]= convert_command[i+3];
    if((restore_command[4]-48)*100 + (restore_command[5]-48)*10 + (restore_command[6]-48)*1 > 255){
      restore_command[4] = '2';
      restore_command[5] = '5';
      restore_command[6] = '5';
    }
  }
  restore_command[8] = 0;

  similarity = get_start_ch + get_end_ch + get_speed_level + get_car_num + get_direction + get_separation;
  if(similarity == 6){
    restore_finished = 0;
  }
  else if(similarity >= 2 and similarity < 6){ 
    //maybe a command with noisy, need restore
      for(i=0; i<9; i++){
        convert_command[i] = restore_command[i];
      }
      restore_finished = 1;
    }
  else{
    restore_finished = -1;
  }
  Serial.print("similarity:");
  Serial.print(similarity);
  Serial.print("restoring!");
  Serial.print(restore_command);
  Serial.print("\n");
  return restore_finished;

}

void backup(){
  for(int i=0; i<9; i++){
    backup_command[i] = convert_command[i];
  }
  return ;
}

void use_backup(){
  for(int i=0; i<9; i++){
    convert_command[i] = backup_command[i];
  }
  return ;
}

void try_ask_server(){
  if(incomeUp == 0){
    Serial.print("backup at beginning!\n");
    BT.write(wifi_command_set[7]);
    delay(50);
    BT.write("3bk\n");
    delay(10);
    incomeUp = millis();
    return ;}
  else if(millis() - incomeUp > income_Every){
    use_backup();
    Serial.print("backup!\n");
    BT.write(wifi_command_set[7]);
    delay(50);
    BT.write("3bk\n");
    delay(10);
    incomeUp = millis();
    }
  return ;   
}

void reConnect(){
  int reCon = 0;
  int cleanstop = 0;
  while(reCon == 0){
      BT.write(wifi_command_set[6]);
      delay(3000);
       while(BT.available()){
      tmp_ch = BT.read();
      Serial.write(tmp_ch);
       }
       
      BT.write(wifi_command_set[7]);
      delay(3000);
       while(BT.available()){
      tmp_ch = BT.read();
      Serial.write(tmp_ch);
       }
       
      BT.write(wifi_command_set[8]);
      delay(3000);
      while(BT.available()){
      tmp_ch = BT.read();
      Serial.write(tmp_ch);
      if(tmp_ch == 'R'){
        tmp_ch = BT.read();
          if(tmp_ch == 'e'){
            cleanstop++;
          }
          tmp_ch = BT.read();
          if(tmp_ch == 'c'){
            cleanstop++;
          }
          tmp_ch = BT.read();
          if(tmp_ch == 'v'){
            cleanstop++;
          }
           if(cleanstop == 3){
             reCon = 1;
             break;
           }
        }
      }
  }  
}



