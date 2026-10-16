#include <MD_Parola.h>
#include <MD_MAX72xx.h>
#include <SPI.h>
MD_Parola matrix(MD_MAX72XX::FC16_HW,10,4);
void setup(){matrix.begin();matrix.setIntensity(2);matrix.displayClear();matrix.displayText("TVQ - IOT",PA_LEFT,70,800,PA_SCROLL_LEFT,PA_SCROLL_LEFT);}
void loop(){if(matrix.displayAnimate())matrix.displayReset();}
