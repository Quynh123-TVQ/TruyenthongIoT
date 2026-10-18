# Bài TH13 — CoAP, ảnh và mã nguồn

Mở [BTH13.md](BTH13.md) để đọc đầy đủ.

## Chạy ngay trên PC

Mở hai terminal ở thư mục code:

Terminal 1:

```bash
node server.cjs
```

Terminal 2:

```bash
python client.py post-non --payload "temp=30.5"
python client.py con
python client.py block
```

Node.js và Python cần cài trước. Không cần npm install/pip install. Script không tạo website; theo dõi kết quả trong terminal và Wireshark.

## ESP

Mở code/esp32_coap/esp32_coap.ino bằng Arduino IDE. Sao config.example.h thành config.local.h, điền Wi-Fi và IP server. Đọc mục 5 của BTH13.md trước khi Upload. Mặc định LAB_MODE=5 gửi NON POST mô phỏng.

## Kiểm tra PC

Đóng server demo trước, chạy từ gốc bộ bài:

```bash
python tests/test_coap.py
```

Giữ nguyên images/code/tests khi đưa lên GitHub. VS Code xem bài có ảnh bằng Ctrl+Shift+V.
