# Kiểm tra và giới hạn

Ngày tạo bộ bài: 16/10/2026. Môi trường chạy PC: Linux, Python 3.12.14, Node.js 24.19.0. Các kết quả sau là thử nghiệm phần mềm PC, không phải dữ liệu phần cứng của người dùng.

| Phần | Đã kiểm tra | Kết quả |
|---|---|---|
| CoAP | CON/NON, retry sau proxy bỏ phản hồi đầu, Observe/cancel, Block2 2048 byte | Đạt trong các integration test loopback |
| Block2 | Ghép đủ 2048 byte và so nội dung/digest | SHA256 `3332c0e3907197cc480ce46dacf74dc38ef2085658546aa6e64e1925e1d5df37` của payload thử TVQ-IOT- lặp |
| Replay PC | Lệnh đầu, replay, sửa seq/time, hết hạn, mở lại DB | Chấp nhận lệnh mới, chặn trùng/sai chữ ký/hết hạn, giữ sequence bền vững |
| FlowMonitor parser | Đơn vị thời gian ns, loss, mean delay, throughput từ XML fixture | Đạt; fixture là dữ liệu test nhân tạo, không phải kết quả mô phỏng LTE |
| MQTT PC | Simulator nhận ON và publish state; subscriber mới nhận retained OFF; kill client tạo LWT OFFLINE; tải hữu hạn | Đạt với broker kiểm thử aMQTT 0.12.1 trên loopback 18884, Paho 2.1.0 |
| Web–Serial | Node HTTP → pseudo terminal → phản hồi STATE ON qua WebSocket; JSON telemetry; disconnect | Đạt bằng PTY Linux giả lập board; chưa thử cổng SPP Windows hoặc HC-05 thật |
| JavaScript / Python / shell | `node --check`, `compileall`, `bash -n` | Đạt cho source tương ứng; không thay thế kiểm tra trình duyệt hoặc Arduino |
| YAML | Parser đọc các cấu hình kể cả tag !secret | Đạt cú pháp YAML; chưa chạy ESPHome validate/compile với secrets thật |
| Chứng chỉ TLS | Chạy script OpenSSL, verify CA + localhost/SAN IP ví dụ | Đạt; chưa kết nối MQTT TLS tới Mosquitto/ESP thật |
| Tài liệu | Liên kết nội bộ, 31 mục, 31 sơ đồ bước, 7 sơ đồ dây, 11 PDF chính | Đã đối chiếu; PDF chính 85 trang ở thời điểm đóng gói |
| Layout PDF | Render toàn bộ 85 trang, xem contact sheet và kiểm tra biên chữ | Không thấy chữ vượt trang/cắt khối; ảnh gốc chỉ có độ phân giải của tài liệu nguồn |

## Phần cần kiểm tra trên máy người dùng

- Arduino/ESP: chưa có `arduino-cli` và toolchain/core board trong môi trường bàn giao, nên **chưa biên dịch hoặc nạp các sketch Uno/ESP**. Cần Verify trước Upload, chọn đúng board/core/thư viện, chạy mạch và giữ log.
- Proteus / Packet Tracer: chưa chạy GUI và chưa tạo project `.pdsprj`/`.pkt`. Các bước dựng mạch/mạng và mã/CLI/bảng IP được cung cấp để dựng lại.
- Zigbee: chưa bắt mạng người dùng; không có PAN ID, địa chỉ, key hoặc PCAPNG thực tế của người dùng. Không lấy ảnh đề thay minh chứng đo.
- NS-3 / NetAnim: chưa build/chạy source LTE trong môi trường này; chưa có XML simulation/độ trễ/thông lượng đo thực. Parser đã có test riêng.
- ESPHome/Home Assistant: chưa validate bằng ESPHome, nạp board hoặc thử automation trên hệ thống người dùng. YAML cần secrets và entity_id thật.
- Trình duyệt: thử khởi chạy kiểm tra UI tự động bị chặn vì thiếu binary Chromium; tải binary không thành công trong môi trường. Đã kiểm cú pháp JavaScript và API/Serial/WebSocket, **chưa kiểm hành vi DOM/canvas trên trình duyệt thật**.
- Raw packet capture không được môi trường cấp quyền, nên không tạo tệp PCAPNG minh chứng mạng trong bộ này. Các test UDP/TCP là giao tiếp thật trên loopback, còn log không được gọi là capture Wireshark.

## Chạy lại

```bash
python -m unittest discover -s tests -v
```

Hai test tích hợp thêm dùng dependencies kiểm thử riêng:

```bash
python -m pip install -r tests/requirements.txt
python tests/integration_mqtt.py
python tests/integration_serial.py
```

`integration_serial.py` cần Linux PTY và `npm ci` trong `code/bluetooth_web`; test MQTT tự mở broker loopback ở cổng 18884. Test protocols dùng UDP 5683/5684; đóng server demo đang chiếm cổng trước khi chạy. Log các lần kiểm tra trong thư mục `docs/logs/`.

Với phần cứng: không gộp báo cáo “đã qua test PC” với báo cáo “đã kiểm thử trên ESP”. Mẫu BAO_CAO.md có chỗ ghi điều kiện và giới hạn.
