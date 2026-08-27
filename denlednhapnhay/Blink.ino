#define LED1 5
#define LED2 6
#define LED3 7
#define LED4 8
#define MOTOR 13
int leds[] = {LED1, LED2, LED3, LED4}; 

void setup() 
{
  for (int i = 0; i < 4; i++) 
  {
    pinMode(leds[i], OUTPUT);
  }
  pinMode(MOTOR , OUTPUT);
}

void nhapnhaydai() {
  for (int i = 0; i < 4; i++) 
  {
    digitalWrite(leds[i], HIGH);  
    delay(50);                    
    digitalWrite(leds[i], LOW); 
  }
}
void motor()
{
   for (int i = 0; i < 4; i++) 
  {
    digitalWrite(MOTOR, LOW);  
    delay(500);                    
    digitalWrite(MOTOR, HIGH);
  }
}
void loop() 
{
  nhapnhaydai();
}

