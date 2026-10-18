#pragma once
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASS "YOUR_WIFI_PASSWORD"
#define COAP_IP IPAddress(192,168,1,20)
#define COAP_PORT 5683
// 0 GET CON; 1 GET NON; 2 Polling; 3 Observe; 4 Block2;
// 5 POST NON every 5 s (matches screenshot method/type); 6 POST CON every 5 s.
#define LAB_MODE 5
