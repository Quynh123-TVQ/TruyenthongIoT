#pragma once
#define WIFI_SSID "CHANGE_ME"
#define WIFI_PASS "CHANGE_ME"
#define MQTT_HOST "192.168.27.10"
#define MQTT_USER "tvq"
#define MQTT_PASS "CHANGE_ME"
#define MQTT_TLS 0
#define MQTT_PORT 1883
#define RETAIN_STATE 1
#define LED_PIN 4  // external LED + 330 ohm to GND; ESP32-S3
#define RESTORE_LOCAL_STATE 1
// For TLS: set MQTT_TLS=1, MQTT_PORT=8883, MQTT_HOST matching cert SAN.
static const char ROOT_CA[] = R"PEM(-----BEGIN CERTIFICATE-----
REPLACE_WITH_LAB_CA
-----END CERTIFICATE-----)PEM";
