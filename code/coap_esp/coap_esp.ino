// ESP32 Arduino, dependency-free small CoAP GET client for the bundled server.
#include <WiFi.h>
#include <WiFiUdp.h>
#include "config.local.h"
WiFiUDP udp;uint16_t mid=1200;const uint8_t token[2]={0x27,0x14};
uint8_t request[100];size_t requestLen=0;unsigned long sent=0,lastPoll=0;bool pending=false,started=false;uint8_t retries=0;uint16_t blockNo=0,total=0;uint8_t blockSzx=4;bool done=false;
uint8_t firmware[2048];
void sendGet(){
 requestLen=0;request[requestLen++]=LAB_MODE==1?0x52:0x42;request[requestLen++]=1;request[requestLen++]=++mid>>8;request[requestLen++]=mid&255;request[requestLen++]=token[0];request[requestLen++]=token[1];
 uint8_t previous=0;
 if(LAB_MODE==3){request[requestLen++]=0x60;previous=6;}
 const char* paths[2]={LAB_MODE==4?"firmware":"sensor",LAB_MODE==4?nullptr:"temp"};
 for(uint8_t j=0;j<2&&paths[j];j++){uint8_t n=strlen(paths[j]);request[requestLen++]=((11-previous)<<4)|n;memcpy(request+requestLen,paths[j],n);requestLen+=n;previous=11;}
 if(LAB_MODE==4){uint32_t v=(blockNo<<4)|blockSzx;uint8_t n=v>255?2:1;request[requestLen++]=((23-previous)<<4)|n;if(n==2)request[requestLen++]=v>>8;request[requestLen++]=v&255;}
 udp.beginPacket(COAP_IP,COAP_PORT);udp.write(request,requestLen);udp.endPacket();sent=millis();pending=true;retries=0;
}
bool ext(uint8_t x,const uint8_t*b,int n,int&i,int&v){if(x<13){v=x;return true;}if(x==13&&i<n){v=13+b[i++];return true;}if(x==14&&i+1<n){v=269+(b[i]<<8)+b[i+1];i+=2;return true;}return false;}
void receive(){uint8_t b[1400];int n=udp.read(b,sizeof(b));if(n<6||(b[0]>>6)!=1||(b[0]&15)!=2||memcmp(b+4,token,2)||b[1]!=69)return;
 uint8_t type=(b[0]>>4)&3;uint16_t id=(b[2]<<8)|b[3];if(type==2&&id!=mid)return;
 int i=6,opt=0;bool more=false,hasBlock=false;uint32_t block=0;
 while(i<n&&b[i]!=255){uint8_t h=b[i++];int d,l;if(!ext(h>>4,b,n,i,d)||!ext(h&15,b,n,i,l)||i+l>n)return;opt+=d;
 if(opt==23){hasBlock=true;block=0;for(int z=0;z<l;z++)block=(block<<8)|b[i+z];more=block&8;}i+=l;}
 if(i<n)i++;int size=n-i;pending=false;
 Serial.printf("MID=%u type=%u payload=%d\n",id,type,size);
 if(LAB_MODE!=4){Serial.write(b+i,size);Serial.println();return;}
 if(!hasBlock)return;uint8_t szx=block&7;uint32_t offset=(block>>4)*(1u<<(szx+4));
 if(offset!=total||total+size>sizeof(firmware)){Serial.println("Bad block offset/size");done=true;return;}
 memcpy(firmware+total,b+i,size);total+=size;blockSzx=szx;
 if(more){blockNo=(block>>4)+1;sendGet();}else{done=true;bool valid=total==2048;const char *pattern="TVQ-IOT-";for(int j=0;j<total;j++)if(firmware[j]!=pattern[j%8])valid=false;Serial.printf("COMPLETE bytes=%u pattern_ok=%d\n",total,valid);}
}
void setup(){Serial.begin(115200);WiFi.begin(WIFI_SSID,WIFI_PASS);}
void loop(){unsigned long now=millis();if(WiFi.status()!=WL_CONNECTED){delay(1);return;}if(!started){udp.begin(56830);started=true;sendGet();lastPoll=now;}
 if(udp.parsePacket())receive();
 if(pending&&now-sent>2000UL*(1UL<<retries)){
  if(LAB_MODE!=1&&retries<3){retries++;udp.beginPacket(COAP_IP,COAP_PORT);udp.write(request,requestLen);udp.endPacket();sent=now;Serial.println("RETRY same MID");}
  else{pending=false;done=true;Serial.println("TIMEOUT");}
 }
 if(LAB_MODE==2&&!pending&&!done&&now-lastPoll>=2000){lastPoll=now;sendGet();}delay(1);
}
