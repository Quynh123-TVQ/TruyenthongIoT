# Đưa bộ bài lên GitHub của bạn

Bộ bàn giao là thư mục nguồn sẵn để tạo repository. Nó chưa được đẩy lên tài khoản GitHub nào.

## Cách dễ: Upload files

1. Đăng nhập GitHub, tạo repository mới với tên tùy chọn, ví dụ `tvq-truyen-thong-iot`.
2. Chọn Private nếu chỉ dùng học cá nhân. Tạo repo trống hoặc mở repo của chính bạn.
3. Add file → Upload files, kéo nội dung trong thư mục TVQ_TruyenThongIoT vào (không kéo ZIP chưa giải nén).
4. Kiểm tra README, các thư mục BTHxx, code, pdf, assets, docs và tools hiện đủ rồi Commit changes.
5. Mở một mục bài để kiểm tra hình và liên kết. GitHub có giới hạn upload qua web; nếu cả thư mục lớn thì dùng Git hoặc GitHub Desktop.

## Cách Git

Chạy terminal trong thư mục đã giải nén; tự thay URL repo của bạn:

```bash
git init
git add .
git commit -m "Them bo thuc hanh IoT TVQ"
git branch -M main
git remote add origin https://github.com/TEN_CUA_BAN/TEN_REPO.git
git push -u origin main
```

Nếu repo đã có lịch sử, clone repo của bạn trước rồi chép các tệp vào; không force push để ghi đè lịch sử. Các tệp config.local.h/secrets.yaml và dữ liệu nhạy cảm đã có mẫu gitignore; vẫn tự kiểm tra trước commit.

Mục NGUON.md giữ nguồn yêu cầu và nguồn hình. Đừng xóa nguồn rồi nhận ảnh gốc của người khác thành ảnh thử nghiệm của mình.
