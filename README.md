# GramDrive - Secure Telegram Cloud Storage Manager

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![GUI Framework](https://img.shields.io/badge/UI-PySide6%20%2F%20Qt6-orange.svg)](https://doc.qt.io/qtforpython-6/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**GramDrive** là ứng dụng khách (Client) trên máy tính chạy hệ điều hành Windows, giúp biến bộ nhớ lưu trữ của Telegram thành một ổ đĩa đám mây bảo mật, riêng tư với dung lượng không giới hạn hoàn toàn miễn phí. 

Được xây dựng trên triết lý thiết kế **Apple Liquid Glassmorphism** (kính mờ tràn viền cực kỳ sang trọng), GramDrive đem lại trải nghiệm quản lý tệp tin cao cấp và mượt mà, đồng thời bảo mật tuyệt đối dữ liệu cá nhân của bạn thông qua cơ chế mã hóa AES-256 trực tiếp ở phía người dùng (Client-side encryption).

---

## ✨ Điểm Nổi Bật & Tính Năng

### 🎨 Giao diện Kính mờ tràn viền (Liquid Glassmorphism)
- Thiết kế không viền (Frameless Window) kết hợp với các góc bo tròn tinh tế và đổ bóng mềm mại.
- Hiệu ứng kính mờ (Translucent overlay) tạo cảm giác chiều sâu cao cấp trên mọi nền màn hình.
- Hỗ trợ đổi giao diện **Sáng/Tối (Light/Dark Mode)** linh hoạt với sự hòa quyện màu sắc tinh tế, tránh hiện tượng chói mắt.
- Bảng tệp tin dạng kính phẳng với thanh chọn liền mạch không đứt đoạn (Continuous Table Highlights).

### 🚀 Lưu trữ Không Giới Hạn & Thuật toán Phân mảnh Thích ứng Thông minh
- **Tự động Phân mảnh Thích ứng (Dynamic Auto-Chunking)**: Hệ thống tự động nhận diện loại máy chủ API bạn đang kết nối:
  - **Official Telegram Bot API (`api.telegram.org`)**: Tự động giới hạn kích thước phân mảnh tối đa là **49 MB** (dưới hạn mức 50MB của Telegram) để đảm bảo tệp tải lên **không bao giờ bị lỗi**. Bạn có thể upload các tệp tin từ vài MB đến hàng chục GB hoàn toàn ổn định và mượt mà!
  - **Local Bot API Server (Tự dựng)**: Tự động mở khóa giới hạn dung lượng phân đoạn lên đến **2 GB** (mốc tối đa Telegram cho phép) hoặc tùy chỉnh linh hoạt để đạt tốc độ tối đa.
- **Tối ưu hóa Tốc độ Đa luồng Song song (Concurrent Transfer)**: Tự động truyền tải lên/xuống song song 3 phân đoạn cùng lúc (Sử dụng Async Semaphores & Concurrent Tasks), giúp nhân gấp 3 lần tốc độ truyền tải tệp tin so với cơ chế tuần tự thông thường.
- Tự động ghép nối nguyên vẹn, kiểm tra tính toàn vẹn (checksum) các phân đoạn khi tải xuống.
- Quản lý hàng chờ tải lên/tải xuống đa luồng chạy ngầm với thanh tiến độ thời gian thực.
- Kéo và thả (Drag & Drop) tệp tin trực tiếp để tải lên vô cùng nhanh chóng.

### 🔒 Bảo mật Tuyệt Đối với Mã hóa AES-256 Đầu Cuối
- Dữ liệu được mã hóa trực tiếp bằng thuật toán **AES-256-CBC** ngay trên máy tính của bạn trước khi đẩy lên Telegram.
- Ngăn chặn hoàn toàn việc Telegram quét hoặc đọc nội dung tệp tin của bạn. Không ai có thể giải mã nếu không có mật khẩu Master Key do bạn giữ.

### 🛠️ Lắng Nghe Lệnh Bot Tự Động (Auto-Listener)
- Tích hợp bộ lắng nghe cập nhật lệnh Telegram trực tiếp.
- Người dùng chỉ cần nhấn **Bắt đầu lắng nghe** trên cài đặt ứng dụng rồi gửi lệnh `/id` tới Bot cá nhân trên Telegram. Hệ thống sẽ tự động bắt lấy mã **Chat ID** của bạn để cấu hình kết nối tự động.
- Kiểm tra kết nối nhanh chóng (Test Bot Connection) bằng một chạm.

### 🌐 Bản Địa Hóa Động Toàn Diện
- Hỗ trợ song ngữ **Tiếng Việt** và **Tiếng Anh**.
- Chuyển đổi ngôn ngữ tức thời không cần khởi động lại ứng dụng, đồng bộ toàn bộ giao diện từ menu, bảng dữ liệu, tiêu đề cho đến các hộp thoại cảnh báo và popup hệ thống.

### 📁 Quản lý Dữ liệu Tiện Lợi
- **Dashboard**: Thống kê trực quan dung lượng đã sử dụng, số lượng tệp tin và biểu đồ danh mục định dạng tệp tin.
- **File Explorer**: Duyệt tệp tin dạng danh sách, tìm kiếm thời gian thực, xóa tệp tin, sao chép link tệp tin.
- **Backup & Restore**: Hỗ trợ xuất/nhập danh sách tệp tin (Metadata) và sao lưu/khôi phục toàn bộ cấu hình cài đặt chỉ bằng 1 file JSON duy nhất.

---

## 🛠️ Yêu cầu Hệ thống

- **Hệ điều hành**: Windows 10 hoặc Windows 11.
- **Python**: Phiên bản 3.11.9 (Khuyến nghị để chạy từ mã nguồn).

---

## 📦 Hướng Dẫn Cài Đặt & Sử Dụng

### Cách 1: Sử dụng Bản đóng gói sẵn (`GramDrive.exe`) - Khuyên dùng cho Người dùng
1. Truy cập vào trang [Releases của GramDrive](https://github.com/tomyrese/gramdrive/releases).
2. Tải về file `GramDrive.exe` phiên bản mới nhất.
3. Chạy trực tiếp tệp tin `GramDrive.exe` để mở ứng dụng (Không cần cài đặt Python hay các thư viện phụ thuộc).

---

### Cách 2: Chạy từ Mã nguồn (Cho Lập trình viên)

**1. Clone dự án về máy tính:**
```bash
git clone https://github.com/tomyrese/gramdrive.git
cd gramdrive
```

**2. Cài đặt các thư viện phụ thuộc:**
```bash
pip install -r requirements.txt
```

**3. Khởi chạy ứng dụng:**
```bash
python main.py
```

---

## ⚙️ Quy trình Thiết Lập Cài Đặt Chi Tiết

Để ứng dụng GramDrive kết nối và hoạt động chính xác với ổ đĩa Telegram của bạn, hãy làm theo các bước dưới đây:

### Bước 1: Tạo Telegram Bot cá nhân
1. Mở ứng dụng Telegram, tìm kiếm tài khoản **@BotFather** (tài khoản bot chính chủ của Telegram có tích xanh).
2. Gửi lệnh `/newbot` và thực hiện theo hướng dẫn để đặt tên hiển thị và tên người dùng (username) cho Bot của bạn.
3. Lưu lại chuỗi ký tự **Bot Token** được cấp (Ví dụ: `1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ`).

### Bước 2: Cấu hình trên GramDrive
1. Khởi chạy GramDrive, truy cập vào menu **Cài đặt** (Settings) ở thanh menu bên trái.
2. Dán mã **Bot Token** bạn vừa tạo ở Bước 1 vào ô nhập liệu tương ứng.
3. Nhấp chọn nút **Bắt đầu lắng nghe** (Start Bot Listener).
4. Mở ứng dụng Telegram trên điện thoại hoặc máy tính, truy cập vào Bot cá nhân của bạn và nhấn **Start** hoặc gửi tin nhắn lệnh `/id`.
5. GramDrive sẽ tự động bắt Chat ID của bạn và hiển thị lên ô **Chat ID** trên màn hình.
6. Nhấp chọn nút **Kiểm tra kết nối** (Test Connection). Một thông báo popup chúc mừng kết nối thành công sẽ hiển thị, đồng thời trạng thái Sidebar sẽ chuyển sang màu xanh lá **Hoạt động (Active)**.

### Bước 3: Lưu trữ cấu hình và Trải nghiệm
1. Tùy chỉnh các thông số:
   - **Mã hóa dữ liệu**: Tích chọn và đặt mật khẩu Master Key nếu muốn bảo mật tệp tin tuyệt đối.
   - **Kích thước phân đoạn (Chunk size)**: Chọn dung lượng tệp tin phân đoạn mong muốn. Hệ thống sẽ tự động clamp về mức an toàn 49MB khi phát hiện kết nối tới Official API.
   - **Ngôn ngữ**: Chọn ngôn ngữ Tiếng Việt hoặc English.
2. Nhấn **Lưu cài đặt** (Save Settings).
3. Bây giờ bạn đã có thể chuyển sang trang **Explorer** để kéo thả tệp tin hoặc duyệt các tệp tin lưu trữ đám mây!

---

## 📂 Cấu Trúc Mã Nguồn Dự Án

```text
GramDrive/
├── config/
│   └── themes/              # Các tệp định nghĩa giao diện QSS (Light / Dark Mode)
├── core/
│   ├── cache_manager.py     # Quản lý thư mục tạm và tự động dọn dẹp cache
│   ├── chunk_manager.py     # Phân mảnh tệp tin lớn và lắp ráp lại khi tải xuống
│   ├── database.py          # Quản lý cơ sở dữ liệu SQLite cục bộ (Cài đặt & Metadata)
│   ├── downloader.py        # Tiến trình xử lý tải xuống tệp nền đa luồng
│   ├── encryptor.py         # Mã hóa và giải mã tệp tin AES-256-CBC
│   ├── file_manager.py      # Trình điều phối trung tâm dữ liệu và quét trạng thái AI
│   ├── telegram_client.py   # Xử lý kết nối API Telegram, tải tệp và Bot Listener
│   └── uploader.py          # Tiến trình xử lý tải lên tệp nền đa luồng với Auto-Chunking thích ứng
├── gui/
│   ├── dashboard_page.py    # Trang thống kê biểu đồ tròn, dung lượng và tệp tin
│   ├── download_page.py     # Trang hiển thị hàng chờ tải xuống tệp tin
│   ├── explorer_page.py     # Trang duyệt tệp tin, tìm kiếm, xuất/nhập sao lưu
│   ├── main_window.py       # Khung giao diện chính tràn viền (Acrylic Glass Shell)
│   ├── settings_page.py     # Trang cấu hình Bot Token, Chat ID, Mã hóa, Ngôn ngữ, Chunk size mở rộng
│   ├── translations.py      # Bộ dịch đa ngôn ngữ và các lớp Hộp thoại tùy chỉnh
│   └── upload_page.py       # Trang kéo thả và chọn tệp tin tải lên đám mây
├── database/                # Thư mục lưu cơ sở dữ liệu SQLite (.gitkeep)
├── temp/                    # Thư mục chứa các phân đoạn tệp tin tạm (.gitkeep)
├── logs/                    # Thư mục ghi nhận nhật ký hệ thống (.gitkeep)
├── main.py                  # Điểm khởi chạy ứng dụng (Entrypoint + Splash Screen)
├── requirements.txt         # Danh sách thư viện Python phụ thuộc
├── icon.ico                 # Biểu tượng của ứng dụng
├── .gitignore               # Tệp tin cấu hình bỏ qua khi đẩy lên git
└── README.md                # Hướng dẫn chi tiết này
```

---

## 🧰 Công Nghệ Sử Dụng

- **Ngôn ngữ**: Python 3.11+
- **Framework GUI**: PySide6 (Qt for Python 6) với phong cách thiết kế QSS hiện đại.
- **Xử lý bất đồng bộ**: `asyncio` & `qasync` (Kết hợp mượt mà vòng lặp sự kiện Qt với Asynchronous Python).
- **Mã hóa**: `pycryptodome` (Cung cấp giải pháp mã hóa AES-256 chuẩn quân đội).
- **Truy cập mạng**: `aiohttp` (Giúp tải lên/xuống các tệp dung lượng cực lớn song song tốc độ cao không nghẽn luồng GUI).
- **Đóng gói**: `PyInstaller`.

---

## ⚠️ Lưu Ý Quan Trọng Về Giới Hạn Tệp Tin Của Telegram
- Với máy chủ Bot API mặc định của Telegram, hạn mức tối đa cho mỗi phần tệp tin tải lên là **50 MB**. Nhờ thuật toán **Dynamic Auto-Chunking** của GramDrive, các tệp tin lớn của bạn sẽ tự động phân tách thành các phần **49 MB** để vượt qua hạn mức này hoàn hảo mà không cần can thiệp thủ công.
- Nếu bạn có máy chủ **Telegram Local Bot API Server** riêng, ứng dụng sẽ mở rộng giới hạn này để tải lên các phần tệp tin lớn lên tới **2 GB** (mốc tối đa Telegram cho phép).
- Ứng dụng hoạt động hoàn toàn cục bộ trực tiếp trên máy của bạn và không truyền bất kỳ thông tin nhạy cảm (như Bot Token, Key mã hóa) về bất kỳ máy chủ bên thứ ba nào.

---

## 📝 Giấy Phép (License)

Dự án này được cấp phép dưới dạng **MIT License**. Bạn có toàn quyền sử dụng, sửa đổi và phân phối phục vụ mục đích cá nhân hoặc thương mại. Xem chi tiết tại tệp [LICENSE](LICENSE) (nếu có).

*Chúc bạn có những trải nghiệm lưu trữ đám mây tuyệt vời và bảo mật cùng GramDrive!*
