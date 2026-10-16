#include <SoftwareSerial.h>
#include <DHT.h>
SoftwareSerial bt(10,11);DHT dht(2,DHT11);unsigned long last=0;
void setup(){Serial.begin(115200);bt.begin(9600);dht.begin();}
void loop(){if(millis()-last<2000)return;last=millis();float t=dht.readTemperature(),h=dht.readHumidity();if(isnan(t)||isnan(h)){Serial.println("DHT error");return;}
 bt.print("{\"temp\":");bt.print(t,1);bt.print(",\"hum\":");bt.print(h,1);bt.println("}");
 Serial.print(t);Serial.print(" C ");Serial.println(h);
}
