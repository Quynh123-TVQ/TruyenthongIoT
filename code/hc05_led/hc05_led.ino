#include <SoftwareSerial.h>
SoftwareSerial bt(10,11);char line[20];uint8_t used=0;
void setup(){Serial.begin(115200);bt.begin(9600);pinMode(13,OUTPUT);}
void loop(){while(bt.available()){char ch=bt.read();if(ch=='\r')continue;
 if(ch=='\n'){line[used]=0;if(!strcmp(line,"ON")||!strcmp(line,"on")){digitalWrite(13,HIGH);bt.println("STATE ON");}else if(!strcmp(line,"OFF")||!strcmp(line,"off")){digitalWrite(13,LOW);bt.println("STATE OFF");}used=0;}
 else if(used<sizeof(line)-1)line[used++]=ch;else used=0;
}}
