# GramDrive - Secure Telegram Cloud Storage Manager

GramDrive là ứng dụng quản lý ổ đĩa đám mây bảo mật cá nhân hoạt động dựa trên API Telegram, được thiết kế với giao diện kính mờ Apple Liquid Glass cao cấp, hoàn toàn không viền (frameless) và bo tròn các góc tinh tế.

Ứng dụng cho phép biến không gian chat lưu trữ của Telegram Bot thành một ổ đĩa đám mây riêng tư có dung lượng lưu trữ không giới hạn, bảo mật tuyệt đối nhờ cơ chế mã hóa AES-256 đầu cuối trực tiếp từ thiết bị.

---

## Các tính năng nổi bật

- **Giao diện Apple Glassmorphism**: Thiết kế kính mờ cao cấp, hỗ trợ chế độ Sáng/Tối (Light/Dark Mode) và chuyển đổi động theo hệ thống hệ điều hành.
- **Dung lượng tệp tin không giới hạn**: Cơ chế tự động phân tách tệp tin lớn thành các phân đoạn (chunk) nhỏ hơn 50MB trước khi tải lên và tự động ghép nối nguyên vẹn khi tải xuống.
- **Bảo mật tuyệt đối AES-256**: Mã hóa tệp tin trực tiếp phía client (Client-side encryption) bằng mật khẩu Master trước khi đẩy lên đám mây, đảm bảo ngay cả Telegram cũng không thể đọc nội dung tệp tin của bạn.
- **Lắng nghe lệnh Bot tự động**: Tích hợp bộ lắng nghe cập nhật lệnh Telegram trực tiếp. Người dùng chỉ cần gửi lệnh `/id` đến bot để lấy mã Chat ID cá nhân một cách nhanh chóng.
- **Bản địa hóa động (VI/EN)**: Dịch chuyển đổi động toàn diện giao diện từ ngoài vào trong bao gồm bảng dữ liệu, tiêu đề và gợi ý nhập liệu.
- **Thanh chọn không đứt đoạn (Continuous Table Highlights)**: Bảng tệp tin hiển thị dạng kính phẳng không viền, làm nổi bật hàng được chọn liên mạch.

---

## Yêu cầu hệ thống

- **Hệ điều hành**: Windows 10/11
- **Python**: Phiên bản 3.11.9 (Khuyến nghị)
- **Telegram Account**: Đã đăng ký và hoạt động.

---

## Hướng dẫn cài đặt và thiết lập nhanh

### Bước 1: Tạo Telegram Bot cá nhân
1. Mở ứng dụng Telegram, tìm kiếm và truy cập vào **@BotFather**.
2. Gửi lệnh `/newbot` và đặt tên cho Bot của bạn.
3. Sao chép chuỗi mã **Bot Token** được cấp (ví dụ: `123456789:ABCdef...`).

### Bước 2: Clone dự án và cài đặt thư viện
1. Tải toàn bộ mã nguồn của dự án về máy tính.
2. Mở terminal tại thư mục dự án và chạy lệnh sau để cài đặt các gói thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```

### Bước 3: Khởi động ứng dụng
Chạy lệnh khởi động giao diện phần mềm:
```bash
python main.py
```

### Bước 4: Thiết lập kết nối đám mây
1. Truy cập vào trang **Settings** (Cài đặt) trên giao diện GramDrive.
2. Dán mã **Bot Token** của bạn vào ô nhập liệu.
3. Bấm **Bắt đầu lắng nghe** (Start Bot Listener).
4. Mở Telegram, truy cập vào Bot cá nhân của bạn và gửi tin nhắn lệnh `/id`. Bot sẽ gửi trả lại mã số **Chat ID** của bạn.
5. Sao chép và dán mã Chat ID đó vào ô **Chat ID** trên trang Cài đặt ứng dụng.
6. Bấm **Test Bot Connection** (Kiểm tra kết nối Bot). Màn hình sẽ hiện popup thông báo kết nối thành công và tự động kích hoạt sidebar về trạng thái **Hoạt động (Active)**.
7. Tùy chỉnh các cấu hình bảo mật, kích thước phân đoạn và bấm **Save Settings** (Lưu cài đặt).

---

## Cấu trúc thư mục dự án

```
GramDrive/
├── config/
│   └── themes/              # File phong cách QSS cho Light và Dark Mode
├── core/
│   ├── cache_manager.py     # Quản lý bộ nhớ đệm và dọn dẹp file tạm
│   ├── chunk_manager.py     # Phân tách và ghép nối tệp tin
│   ├── database.py          # Quản lý cơ sở dữ liệu SQLite cục bộ
│   ├── downloader.py        # Tiến trình tải xuống tệp nền
│   ├── encryptor.py         # Module mã hóa AES-256-CBC
│   ├── file_manager.py      # Bộ điều phối trung tâm tệp tin và AI Scan
│   ├── telegram_client.py   # Client API kết nối Telegram Bot và Poller
│   └── uploader.py          # Tiến trình tải lên tệp nền
├── gui/
│   ├── assets/              # Tài nguyên hình ảnh, biểu tượng logo
│   ├── dashboard_page.py    # Trang bảng điều khiển thống kê dung lượng
│   ├── download_page.py     # Trang hàng chờ tải xuống tệp tin
│   ├── explorer_page.py     # Trang duyệt, tìm kiếm, xuất nhập tệp tin
│   ├── main_window.py       # Khung ứng dụng chính không viền
│   ├── settings_page.py     # Trang quản lý cấu hình và kết nối
│   ├── translations.py      # Từ điển đa ngôn ngữ động và Popup custom
│   └── upload_page.py       # Trang kéo thả tải tệp tin lên
├── database/                # Thư mục chứa sqlite database (.gitkeep)
├── temp/                    # Thư mục chứa file tạm khi tách/ghép (.gitkeep)
├── logs/                    # Thư mục chứa file logs (.gitkeep)
├── main.py                  # Điểm khởi chạy ứng dụng (Entrypoint)
├── requirements.txt         # File mô tả thư viện phụ thuộc
├── .gitignore               # Cấu hình bỏ qua tệp tin rác khi git push
└── README.md                # Tài liệu hướng dẫn sử dụng này
```
