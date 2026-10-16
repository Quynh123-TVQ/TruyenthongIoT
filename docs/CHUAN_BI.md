# Chuẩn bị môi trường

Bộ này chọn cấu hình riêng TVQ và giữ loại thiết bị theo đề. Không cần mua tất cả linh kiện để đọc bài; phần thử thật cần đủ linh kiện của từng mục.

| Phần | Phần cứng / phần mềm | Điểm cần kiểm tra |
|---|---|---|
| UART, RTC, SPI, HC-05 | Uno; ESP8266 cho UART; Arduino IDE | Đúng board, COM, mức điện áp; RX ESP/HC-05 không chịu 5 V |
| Mạng gia đình | Packet Tracer có thiết bị IoT | Tên cổng router và tính năng model có thể khác |
| Zigbee | Sniffer CC2531 + coordinator riêng + thiết bị | Firmware/driver tương ứng đúng ZBOSS COM, không lẫn WinUSB/extcap |
| Wi-Fi | HAOS, ESPHome, Wemos hoặc ESP32-S3 | YAML đúng chip; API key sinh mới; LED S3 dùng LED ngoài GPIO4 |
| LTE | Debian/Ubuntu, NS-3.43, NetAnim | Đĩa host và guest đủ; không dùng terminal HAOS để build NS-3 |
| MQTT/CoAP/bảo mật | ESP32/S3 hoặc demo PC, broker lab, Wireshark | Đúng điểm capture; mô phỏng PC không là số đo thiết bị thật |

## Home Assistant và máy ảo

1. Nếu HA của bạn đã hoạt động, giữ bản cài đang dùng và sao lưu trước thay đổi. Với cài mới, dùng Home Assistant OS trong máy ảo theo trang cài đặt chính thức, chọn image đúng hypervisor.
2. Trong VirtualBox, chọn card mạng phù hợp để PC truy cập HA; bridged thường dễ làm bài LAN hơn NAT, nhưng phụ thuộc mạng. Xem IP HA tại console hoặc DHCP router; truy cập `http://IP_HA:8123`.
3. Chỉ chuyển USB coordinator vào máy ảo cần nó. CC2531 sniffer cho ZBOSS Windows để ở máy Windows chủ. Một thiết bị USB không thể cùng bị hai hệ điều hành chiếm dụng.
4. Cài Mosquitto broker trong HAOS, tạo user MQTT riêng. Cài ESPHome Device Builder để làm bài 8. Tên mục quản lý add-on/app có thể khác bản HA; tìm Mosquitto/ESPHome trong kho ứng dụng của bản cài.
5. Tài liệu cũ dùng Supervised trên hệ điều hành tự quản lý. Phương thức đó đã hết hỗ trợ chính thức; với cài mới chọn HAOS hoặc Container theo nhu cầu. Container không có kho add-on/app như HAOS.
6. Với coordinator dùng Zigbee2MQTT: chọn đúng firmware coordinator và adapter, cấu hình MQTT user/IP, serial path ổn định của dongle; Start rồi pair một thiết bị lab. Không flash firmware sniffer lên coordinator để làm bài 6.

Nguồn: https://www.home-assistant.io/installation/ và thông báo deprecation liệt kê trong NGUON.md. Hướng dẫn chi tiết giao diện thay theo phiên bản, nên lấy log và cấu hình thực tế làm căn cứ.

## Cài thư viện Arduino

Arduino IDE → Boards Manager: **Arduino AVR Boards** cho Uno; **esp8266** cho NodeMCU; **esp32 by Espressif Systems** cho S3. Library Manager:

- RTC: **RTClib** (Adafruit).
- LCD: **LiquidCrystal_I2C** có `init()`/`backlight()`; module LCD mặc định `0x27`, đổi nếu cần.
- SPI matrix: **MD_Parola**, **MD_MAX72XX** (MajicDesigns).
- DHT: **DHT sensor library** (Adafruit), kèm Adafruit Unified Sensor nếu yêu cầu.
- MQTT: **PubSubClient**; HMAC ESP: **ArduinoJson 7**. Preferences, WiFi, WiFiUDP và mbedTLS thuộc core ESP32.

`SoftwareSerial` có trong core AVR; bản ESP8266 cần EspSoftwareSerial tương thích core. Mã Uno và ESP8266 nằm ở các thư mục riêng trùng tên sketch.

Các phiên bản core/thư viện trên máy bạn có thể khác. Nếu Verify lỗi, giữ nguyên log lỗi, tên board và phiên bản rồi đối chiếu; không lấy việc kiểm tra cú pháp PC làm kết quả biên dịch Arduino.

## Phần PC

Python >=3.10 cho các script chính (runtime tạo bộ bài: 3.12). Tạo virtual environment rồi:

```bash
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Linux: source .venv/bin/activate
python -m pip install -r code/mqtt_pc/requirements.txt
```

CoAP server chỉ dùng Node built-in, client CoAP chỉ dùng Python standard library. Bluetooth web dùng Node >=20 và `npm ci` trong `code/bluetooth_web`. OpenSSL dùng cho tạo chứng chỉ TLS.

Khi rebuild tài liệu cần Python packages `reportlab`, `pymupdf`, font DejaVu Sans tại đường dẫn trong `tools/build_materials.py`. Người chỉ đọc PDF/chạy code không cần các thư viện dựng tài liệu.

## Cấu hình riêng

Sao `config.example.h` → `config.local.h` bên trong sketch tương ứng. Sao `secrets.example.yaml` → `secrets.yaml` cho ESPHome. Không commit các tệp đã điền password/key. Các mạng `192.168.27.x`, `10.27.x.x` là ví dụ Packet Tracer, không ép IP máy thật về các giá trị đó.
