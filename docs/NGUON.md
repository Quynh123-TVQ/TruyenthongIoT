# Nguồn, phạm vi và khác biệt

## Nguồn yêu cầu

Tham khảo repository https://github.com/buncric/truyenthongiot tại commit `7a7f6c381cd7ead7ee692d03844f4a6c6ba06cc3` (đọc ngày 16/10/2026).

Bộ đề PDF trong `tai-lieu-goc` của nguồn đó được dùng để xác định mục tiêu, câu hỏi và cách chia bài. Repo nguồn có 11 nhóm, 31 mục nhỏ, không có bài 7/11; mục 2.3 DS1307 trùng nội dung I²C của 3.1. Hướng dẫn nguồn còn có kết quả thử riêng của tác giả; bộ TVQ không nhập các kết quả đó thành kết quả người dùng.

**Phần được viết mới:** toàn bộ guide Markdown TVQ, catalog bước, 31 sơ đồ SVG/PNG, source code trong code/, test protocol và bố cục PDF. Không sao chép toàn bộ repo rồi đổi tên người làm.

**Ảnh trích để đối chiếu thao tác:**

| Tệp trong bộ TVQ | PDF đề gốc trong repo tham khảo | Trang |
|---|---|---|
| assets/source/bth4.jpeg | BTH4_ETHERNET-TCPIP.pdf | 5 |
| assets/source/bth5.png | BTH5_BLUETOOTH.pdf | 8 |
| assets/source/bth6.png | BTH6_ZigBee.pdf | 5 |
| assets/source/bth8.png | BTH8_WiFi.pdf | 6 |
| assets/source/bth12.png | BTH12_MQTT.pdf | 11 |
| assets/source/bth14.png | BTH14_Bao-mat.pdf | 8 |

Các screenshot giữ thông tin của ví dụ trong đề, không phải cấu hình mới TVQ. Ảnh trong PDF được bổ sung mũi tên ở lớp trình bày. Bản 6.1 chi tiết trong docs/ là tài liệu đã tạo trước từ BTH6_ZigBee.pdf người dùng gửi, chứa 4 ảnh gốc có nguồn. Không gán quyền sở hữu ảnh gốc cho bộ mã mới. Repo tham khảo không có LICENSE ở gốc khi kiểm tra; bộ này không tự cấp giấy phép cho tài sản của bên thứ ba.

## Tài liệu kỹ thuật chính thức

- CoAP base: https://www.rfc-editor.org/rfc/rfc7252
- Observe: https://www.rfc-editor.org/rfc/rfc7641
- Blockwise: https://www.rfc-editor.org/rfc/rfc7959
- ZBOSS / CC2531, khóa Wireshark: https://www.zigbee2mqtt.io/advanced/zigbee/04_sniff_zigbee_traffic.html
- ZBOSS package: https://dsr-iot.com/files-info/zboss-sniffer/
- Wireshark MAC filter: https://www.wireshark.org/docs/dfref/w/wpan.html
- Wireshark Zigbee NWK: https://www.wireshark.org/docs/dfref/z/zbee_nwk.html
- Wireshark View / Capture: https://www.wireshark.org/docs/wsug_html_chunked/ChUseViewMenuSection.html và https://www.wireshark.org/docs/wsug_html_chunked/ChUseCaptureMenuSection.html
- ESPHome OTA và cổng mặc định: https://esphome.io/components/ota/esphome/
- ESPHome thay đổi OTA platform: https://esphome.io/components/ota/
- Home Assistant installation: https://www.home-assistant.io/installation/
- HA Supervised deprecation: https://www.home-assistant.io/blog/2025/05/22/deprecating-core-and-supervised-installation-methods-and-32-bit-systems/
- NS-3 LTE/EPC API và mô hình: https://www.nsnam.org/docs/models/html/lte-user.html
- Paho MQTT Python API v2: https://eclipse.dev/paho/clients/python/docs/
- ESP32 Preferences/NVS: https://docs.espressif.com/projects/arduino-esp32/en/latest/api/preferences.html

Đã đối chiếu các trang trên ngày 16/10/2026. Tên mục giao diện và API có thể khác phiên bản phần mềm người học cài.

## Những điểm riêng có ý nghĩa

- UART dùng hai đường debug/link và ACK có kết thúc dòng; mô tả chia áp RX ESP.
- Báo thức có lưu EEPROM, menu bốn nút, giới hạn chuông và chặn lặp trong cùng phút.
- Packet Tracer đổi toàn bộ kế hoạch IP/SSID TVQ, dùng một tài khoản nhất quán; có cách kiểm tra từng chặng.
- HC-05 dùng Classic SPP qua backend Serial; không khẳng định Web Bluetooth BLE truy cập được HC-05 trực tiếp.
- ESPHome có Wemos đúng đề và biến thể S3 dùng LED ngoài; OTA 8266/3232 được phân biệt.
- MQTT tách cmd/state/availability và NVS khỏi broker retain; dữ liệu giả lập được đánh dấu.
- CoAP triển khai client/server tối giản riêng cho demo, có CON/NON, retry, Observe và nhận đủ Block2; không nhận là stack sản xuất đầy đủ RFC.
- TLS kiểm CA/SAN và đồng hồ; chống replay dùng HMAC + time + sequence bền vững, không chỉ kiểm timestamp.
- Tính sẵn sàng dùng tải nhẹ hữu hạn và ngắt broker/AP lab, không thực hiện RF jamming/deauth.

Các kiểm tra đã chạy và giới hạn được ghi trong KIEM_THU.md. Không bổ sung file PCAPNG/HEX/.pkt/.pdsprj giả để tạo cảm giác đã làm thực nghiệm.
