#include <Wire.h>
#include <RTClib.h>
#include <LiquidCrystal_I2C.h>
#include <EEPROM.h>
RTC_DS1307 rtc;LiquidCrystal_I2C lcd(0x27,16,2);
struct Alarm{uint8_t magic,h,m,on;} alarm;
const uint8_t pins[]={2,3,4,5};bool state[]={1,1,1,1},rawPrev[]={1,1,1,1};
unsigned long edge[4]={},pressed[4]={};bool longDone[4]={};
uint8_t mode=0,field=0,editH=0,editM=0;bool ringing=false;uint32_t firedMinute=0;
unsigned long ringAt=0,screenAt=0;
void saveAlarm(){EEPROM.put(0,alarm);}
void tap(uint8_t k){
 if(ringing){ringing=false;noTone(8);return;}
 if(k==0){mode=(mode+1)%3;field=0;DateTime t=rtc.now();editH=(mode==1?alarm.h:t.hour());editM=(mode==1?alarm.m:t.minute());return;}
 if(!mode)return;
 if(k==1||k==2){int n=(k==1?1:-1);if(!field)editH=(editH+24+n)%24;else editM=(editM+60+n)%60;}
 if(k==3){if(field==0)field=1;else{if(mode==1){alarm.h=editH;alarm.m=editM;saveAlarm();}else{DateTime t=rtc.now();rtc.adjust(DateTime(t.year(),t.month(),t.day(),editH,editM,0));}mode=0;}}
}
void setup(){Serial.begin(115200);Wire.begin();lcd.init();lcd.backlight();pinMode(8,OUTPUT);
 for(auto p:pins)pinMode(p,INPUT_PULLUP);
 if(!rtc.begin()){lcd.print("RTC missing");while(true)delay(100);}
 if(!rtc.isrunning())rtc.adjust(DateTime(F(__DATE__),F(__TIME__)));
 EEPROM.get(0,alarm);if(alarm.magic!=0xA7||alarm.h>23||alarm.m>59||alarm.on>1){alarm={0xA7,7,0,0};saveAlarm();}}
void loop(){unsigned long ms=millis();
 for(uint8_t k=0;k<4;k++){bool r=digitalRead(pins[k]);if(r!=rawPrev[k]){rawPrev[k]=r;edge[k]=ms;}
  if(ms-edge[k]>=30&&r!=state[k]){state[k]=r;if(!r){pressed[k]=ms;longDone[k]=false;}else if(!longDone[k])tap(k);}
  if(k==0&&!state[k]&&!longDone[k]&&ms-pressed[k]>=2000){longDone[k]=true;if(ringing){ringing=false;noTone(8);}else{alarm.on=!alarm.on;saveAlarm();}}
 }
 DateTime t=rtc.now();uint32_t minute=t.unixtime()/60;
 if(alarm.on&&t.hour()==alarm.h&&t.minute()==alarm.m&&firedMinute!=minute){firedMinute=minute;ringing=true;ringAt=ms;tone(8,2000);}
 if(ringing&&ms-ringAt>=30000){ringing=false;noTone(8);}
 if(ms-screenAt>=250){screenAt=ms;char s[17];lcd.setCursor(0,0);
  if(mode)snprintf(s,sizeof(s),"%s %02u:%02u %c",mode==1?"ALARM":"CLOCK",editH,editM,field?'M':'H');
  else snprintf(s,sizeof(s),"%02u:%02u:%02u",t.hour(),t.minute(),t.second());
  lcd.print("                ");lcd.setCursor(0,0);lcd.print(s);
  snprintf(s,sizeof(s),"AL %02u:%02u %s",alarm.h,alarm.m,alarm.on?"ON":"OFF");lcd.setCursor(0,1);lcd.print("                ");lcd.setCursor(0,1);lcd.print(s);
 }
}
