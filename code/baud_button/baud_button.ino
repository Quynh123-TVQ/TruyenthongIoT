// UNO: button D2 to GND, LED D13. UART under test = hardware Serial.
const uint8_t BUTTON=2;bool stable=HIGH,lastRaw=HIGH,config=false,held=false;
unsigned long changed=0,down=0,lastClick=0,blinkAt=0;uint8_t clicks=0,pulses=0;
unsigned long selected=9600;bool lit=false;
void flash(uint8_t n){pulses=n*2;blinkAt=millis();lit=false;digitalWrite(13,LOW);}
void setup(){pinMode(BUTTON,INPUT_PULLUP);pinMode(13,OUTPUT);Serial.begin(selected);}
void loop(){
 unsigned long now=millis();bool raw=digitalRead(BUTTON);
 if(raw!=lastRaw){lastRaw=raw;changed=now;}
 if(now-changed>=30&&raw!=stable){
  stable=raw;
  if(!stable){down=now;held=false;}
  else if(!held&&config){clicks++;lastClick=now;}
 }
 if(!stable&&!held&&now-down>=3000){
  held=true;config=!config;clicks=0;
  if(config){Serial.println("CONFIG: one=9600, double=115200");flash(6);}
  else{Serial.print("Applying baud: ");Serial.println(selected);Serial.flush();Serial.end();Serial.begin(selected);Serial.println("RUN");flash(2);}
 }
 if(config&&clicks&&now-lastClick>450&&stable){
  if(clicks==1){selected=9600;flash(1);}else{selected=115200;flash(2);}
  Serial.print("Selected baud (applied on exit): ");Serial.println(selected);clicks=0;
 }
 if(pulses&&now-blinkAt>=100){blinkAt=now;lit=!lit;digitalWrite(13,lit);pulses--;if(!pulses)digitalWrite(13,LOW);}
}
