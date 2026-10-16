#include <WiFi.h>
#include <time.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <Preferences.h>
#include <esp_task_wdt.h>
#include <esp_idf_version.h>
bool wdtSubscribed=false;
void startWatchdog(){
#if ESP_IDF_VERSION_MAJOR >= 5
 esp_task_wdt_config_t cfg={};cfg.timeout_ms=10000;cfg.idle_core_mask=0;cfg.trigger_panic=true;
 esp_err_t err=esp_task_wdt_init(&cfg);if(err==ESP_ERR_INVALID_STATE)esp_task_wdt_reconfigure(&cfg);
#else
 esp_task_wdt_init(10,true);
#endif
 wdtSubscribed=esp_task_wdt_status(NULL)==ESP_OK || esp_task_wdt_add(NULL)==ESP_OK;
}
#include "config.local.h"
#if MQTT_TLS
WiFiClientSecure transport;
#else
WiFiClient transport;
#endif
PubSubClient mqtt(transport);Preferences nv;
bool led=false;unsigned long retryAt=0,sampleAt=0,lastCommand=0;bool received=false;
void report(){mqtt.publish("tvq/lab12/state",led?"ON":"OFF",RETAIN_STATE);}
void setLed(bool v){if(v!=led){led=v;if(RESTORE_LOCAL_STATE)nv.putBool("on",v);}digitalWrite(LED_PIN,led);}
void onMessage(char* topic,byte* data,unsigned int n){
 if(n>16)return;unsigned long now=millis();if(received&&now-lastCommand<100)return;
 received=true;lastCommand=now;
 if(n==2&&!memcmp(data,"ON",2))setLed(true);
 else if(n==3&&!memcmp(data,"OFF",3))setLed(false);
 else if(n==6&&!memcmp(data,"TOGGLE",6))setLed(!led);
 else return;report();
}
void setup(){Serial.begin(115200);startWatchdog();pinMode(LED_PIN,OUTPUT);nv.begin("tvq-led",false);led=RESTORE_LOCAL_STATE?nv.getBool("on",false):false;digitalWrite(LED_PIN,led);
 WiFi.mode(WIFI_STA);WiFi.begin(WIFI_SSID,WIFI_PASS);
 #if MQTT_TLS
 configTime(0,0,"pool.ntp.org","time.google.com");transport.setCACert(ROOT_CA);
 #endif
 mqtt.setServer(MQTT_HOST,MQTT_PORT);mqtt.setCallback(onMessage);mqtt.setKeepAlive(15);mqtt.setSocketTimeout(2);mqtt.setBufferSize(384);
}
void loop(){if(wdtSubscribed)esp_task_wdt_reset();unsigned long now=millis();
 if(WiFi.status()!=WL_CONNECTED){if(now-retryAt>=5000){retryAt=now;WiFi.reconnect();}delay(1);return;}
 #if MQTT_TLS
 if(time(nullptr)<1700000000){delay(1);return;}
 #endif
 if(!mqtt.connected()){
  if(now-retryAt>=3000){retryAt=now;uint32_t begin=millis();String id="TVQ-"+WiFi.macAddress();
   if(mqtt.connect(id.c_str(),MQTT_USER,MQTT_PASS,"tvq/lab12/availability",1,true,"OFFLINE")){
    mqtt.subscribe("tvq/lab12/cmd");mqtt.publish("tvq/lab12/availability","ONLINE",true);report();mqtt.publish("tvq/lab12/note","boot/reconnect",false);
   }Serial.printf("connect_ms=%lu state=%d\n",(unsigned long)(millis()-begin),mqtt.state());
  }delay(1);return;
 }
 mqtt.loop();if(now-sampleAt>=5000){sampleAt=now;
  // Intentionally generated test data, NOT a physical temperature sensor.
  float t=25.0f+(now/5000%20)/10.0f;char buf[100];snprintf(buf,sizeof(buf),"{\"temp\":%.1f,\"hum\":60,\"simulated\":true}",t);mqtt.publish("tvq/lab12/sensor",buf,false);
 }delay(1);
}
