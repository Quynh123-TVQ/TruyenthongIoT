#include <SoftwareSerial.h>
SoftwareSerial bt(10,11);
void setup(){Serial.begin(115200);bt.begin(38400);Serial.println("HC05 full AT mode: Both NL & CR");}
void loop(){while(Serial.available())bt.write(Serial.read());while(bt.available())Serial.write(bt.read());}
