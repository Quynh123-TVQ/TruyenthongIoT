# Lệnh chạy nhanh trên Windows

Mở PowerShell tại thư mục gốc TVQ_TruyenThongIoT. Những lệnh có `IP_BROKER`, password hoặc đường dẫn cần thay bằng giá trị của bạn.

## CoAP: chạy ngay trên PC không cần ESP

Terminal 1:

```powershell
node .\code\coap\server.cjs
```

Terminal 2:

```powershell
python .\code\coap\client.py con
python .\code\coap\client.py non
python .\code\coap\client.py block
python .\code\coap\client.py observe --seconds 60
```

Block cần báo `complete=2048`. Server mặc định loopback, thích hợp học PC. Để ESP truy cập server, dừng bằng Ctrl+C rồi chạy lại:

```powershell
$env:COAP_HOST="0.0.0.0"
node .\code\coap\server.cjs
```

Điền IP LAN thật của PC trong config.local.h của coap_esp và cho phép UDP 5683 trên firewall lab. Để mất response đầu: chạy `python .\code\coap\loss_proxy.py`, rồi client con/block có `--port 5684`. Proxy chỉ dành thử PC loopback.

## MQTT PC

Cài Mosquitto phù hợp hệ điều hành và đưa lệnh vào PATH. Trước khi chạy broker, chắc chắn không có broker khác giữ cổng 1883.

Terminal broker PC-only:

```powershell
mosquitto -c .\code\mqtt_pc\mosquitto-local.conf -v
```

Terminal simulator:

```powershell
python -m pip install -r .\code\mqtt_pc\requirements.txt
python .\code\mqtt_pc\lab.py device
```

Terminal subscriber / gửi lệnh:

```powershell
python .\code\mqtt_pc\lab.py sub --topic "tvq/lab12/#"
# Mở terminal khác để publish:
python .\code\mqtt_pc\lab.py pub --message ON
python .\code\mqtt_pc\lab.py pub --message OFF
```

Nếu dùng broker HA/LAN có xác thực:

```powershell
$env:MQTT_USER="tvq"
$env:MQTT_PASS="MAT_KHAU_LAB_CUA_BAN"
python .\code\mqtt_pc\lab.py sub --host IP_BROKER --topic "tvq/lab12/#"
```

Loopback broker này không dành ESP qua Wi-Fi. Dùng mosquitto-lan.example.conf đã sửa hoặc broker HA cho ESP.

## Bluetooth web

```powershell
cd .\code\bluetooth_web
npm ci
npm start
```

Mở http://127.0.0.1:3085, Quét cổng → chọn COM → Kết nối. Với sketch LED chọn Bật/Tắt và nhìn log STATE. Với sketch DHT, xem nhiệt độ/đồ thị; nút LED không có chức năng trong sketch DHT.

## Chống replay chạy riêng trên PC

Terminal tại thư mục security:

```powershell
cd .\code\security
$env:TVQ_HMAC_KEY="THAY_BANG_CHUOI_NGAU_NHIEN_RIENG_DAI_IT_NHAT_32_KY_TU"
python .\replay_guard.py demo
```

Kết quả mong đợi: first accepted, replay duplicate, tampered signature. Demo dùng sequence tăng theo thời gian. Không dùng nguyên chuỗi ví dụ này làm khóa thật. Với ESP và mqtt_guard, hai phía phải dùng cùng khóa; sequence sau phải lớn hơn sequence đã lưu. Xem bài 14.2 để thử qua broker.

## Linux

Các lệnh Python/Node tương tự nhưng dùng `/` thay `\`. Biến môi trường đặt bằng `export MQTT_USER=tvq`, `export MQTT_PASS='...'`, `export COAP_HOST=0.0.0.0`. Cài/chạy NS-3 theo bài 9, không chạy trong Home Assistant OS.
