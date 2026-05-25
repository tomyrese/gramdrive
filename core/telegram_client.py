import os
import io
import aiohttp
import asyncio
from typing import Optional, Callable, Any, Dict

class ProgressFile(io.IOBase):
    def __init__(self, file_path: str, callback: Optional[Callable[[int, int], None]] = None):
        super().__init__()
        self.f = open(file_path, "rb")
        self.size = os.path.getsize(file_path)
        self.uploaded = 0
        self.callback = callback

    def read(self, size: int = -1) -> bytes:
        chunk = self.f.read(size)
        self.uploaded += len(chunk)
        if self.callback:
            if asyncio.iscoroutinefunction(self.callback):
                asyncio.create_task(self.callback(self.uploaded, self.size))
            else:
                self.callback(self.uploaded, self.size)
        return chunk

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def seek(self, offset: int, whence: int = 0) -> int:
        res = self.f.seek(offset, whence)
        if offset == 0 and whence == 0:
            self.uploaded = 0
        return res

    def tell(self) -> int:
        return self.f.tell()

    def close(self) -> None:
        self.f.close()
        super().close()

class TelegramClient:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{token}"
        self.file_url = f"https://api.telegram.org/file/bot{token}"
        self.polling_active = False

    async def test_connection(self) -> bool:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.api_url}/getMe") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("ok", False)
                    return False
            except Exception:
                return False

    async def upload_chunk(
        self, 
        chunk_path: str, 
        callback: Optional[Callable[[int, int], None]] = None
    ) -> Optional[Dict[str, Any]]:
        for attempt in range(3):
            try:
                async with aiohttp.ClientSession() as session:
                    data = aiohttp.FormData()
                    data.add_field("chat_id", self.chat_id)
                    
                    pf = ProgressFile(chunk_path, callback)
                    data.add_field(
                        "document", 
                        pf, 
                        filename=os.path.basename(chunk_path)
                    )
                    
                    try:
                        async with session.post(f"{self.api_url}/sendDocument", data=data) as response:
                            if response.status == 200:
                                res_json = await response.json()
                                if res_json.get("ok"):
                                    doc = res_json["result"]["document"]
                                    return {
                                        "message_id": str(res_json["result"]["message_id"]),
                                        "file_id": doc["file_id"]
                                    }
                            await asyncio.sleep(2 ** attempt)
                    finally:
                        pf.close()
            except Exception:
                await asyncio.sleep(2 ** attempt)
        return None

    async def download_chunk(
        self, 
        file_id: str, 
        dest_path: str, 
        callback: Optional[Callable[[int, int], None]] = None
    ) -> bool:
        for attempt in range(3):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.api_url}/getFile", params={"file_id": file_id}) as response:
                        if response.status != 200:
                            continue
                        res_json = await response.json()
                        if not res_json.get("ok"):
                            continue
                        
                        file_path = res_json["result"]["file_path"]
                        download_url = f"{self.file_url}/{file_path}"
                        
                        async with session.get(download_url) as file_response:
                            if file_response.status != 200:
                                continue
                            
                            total_size = int(file_response.headers.get("Content-Length", 0))
                            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                            
                            downloaded = 0
                            with open(dest_path, "wb") as f:
                                async for chunk in file_response.content.iter_chunked(128 * 1024):
                                    f.write(chunk)
                                    downloaded += len(chunk)
                                    if callback:
                                        if asyncio.iscoroutinefunction(callback):
                                            await callback(downloaded, total_size)
                                        else:
                                            callback(downloaded, total_size)
                            return True
            except Exception:
                await asyncio.sleep(2 ** attempt)
        return False

    async def delete_message(self, message_id: str) -> bool:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.api_url}/deleteMessage", 
                    json={"chat_id": self.chat_id, "message_id": int(message_id)}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("ok", False)
                    return False
            except Exception:
                return False

    async def start_polling(self) -> None:
        self.polling_active = True
        offset = 0
        while self.polling_active:
            if not self.token:
                await asyncio.sleep(3)
                continue
            
            try:
                async with aiohttp.ClientSession() as session:
                    url = f"https://api.telegram.org/bot{self.token}/getUpdates"
                    params = {"offset": offset, "timeout": 5}
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get("ok"):
                                for update in data["result"]:
                                    offset = update["update_id"] + 1
                                    message = update.get("message")
                                    if not message:
                                        continue
                                    
                                    text = message.get("text", "").strip()
                                    chat_id = message["chat"]["id"]
                                    
                                    reply_text = ""
                                    if text == "/start":
                                        reply_text = (
                                            f"<b>GramDrive Cloud Node</b>\n\n"
                                            f"Chào mừng bạn đến với GramDrive - Hệ thống quản lý ổ đĩa đám mây cá nhân thông qua Telegram!\n\n"
                                            f"Bot hiện đang đóng vai trò là cổng lưu trữ dữ liệu riêng tư của bạn.\n\n"
                                            f"Các câu lệnh có sẵn:\n"
                                            f"- /id : Lấy mã số Chat ID cá nhân\n"
                                            f"- /help : Xem hướng dẫn cấu hình chi tiết\n"
                                            f"- /status : Xem báo cáo dung lượng ổ đĩa trực tiếp"
                                        )
                                    elif text == "/id":
                                        reply_text = (
                                            f"<b>GramDrive Cloud Node</b>\n\n"
                                            f"Chat ID của bạn là:\n"
                                            f"<code>{chat_id}</code>\n\n"
                                            f"Hãy sao chép mã số trên (chạm vào để copy) và dán vào phần cài đặt của ứng dụng GramDrive Desktop để bắt đầu kết nối."
                                        )
                                    elif text == "/help":
                                        reply_text = (
                                            f"<b>Hướng dẫn cấu hình GramDrive:</b>\n\n"
                                            f"1. Sao chép <b>Bot Token</b> từ @BotFather dán vào GramDrive Desktop.\n"
                                            f"2. Bấm <b>Start Bot Listener</b> trên Desktop.\n"
                                            f"3. Gửi lệnh /id cho bot này để lấy Chat ID cá nhân.\n"
                                            f"4. Sao chép và dán <b>Chat ID</b> vào GramDrive Desktop.\n"
                                            f"5. Bấm <b>Test Bot Connection</b> rồi bấm <b>Save Settings</b> để hoàn tất!"
                                        )
                                    elif text == "/status":
                                        import sqlite3
                                        total_files = 0
                                        total_size = 0
                                        db_exists = False
                                        try:
                                            db_path = "database/telegram_drive.db"
                                            if os.path.exists(db_path):
                                                db_exists = True
                                                conn = sqlite3.connect(db_path)
                                                cursor = conn.cursor()
                                                cursor.execute("SELECT COUNT(DISTINCT hash), SUM(size) FROM files")
                                                row = cursor.fetchone()
                                                total_files = row[0] if row[0] else 0
                                                total_size = row[1] if row[1] else 0
                                                conn.close()
                                        except Exception:
                                            pass
                                        
                                        def get_human_size(size_bytes: int) -> str:
                                            for unit in ['Bytes', 'KB', 'MB', 'GB', 'TB']:
                                                if size_bytes < 1024.0:
                                                    return f"{size_bytes:.2f} {unit}"
                                                size_bytes /= 1024.0
                                            return f"{size_bytes:.2f} PB"
                                            
                                        size_str = get_human_size(total_size)
                                        reply_text = (
                                            f"<b>Báo cáo Trạng thái Ổ đĩa GramDrive:</b>\n\n"
                                            f"- Trạng thái kết nối: Hoạt động ✅\n"
                                            f"- Cơ sở dữ liệu cục bộ: {'Đã kết nối' if db_exists else 'Ngoại tuyến'}\n"
                                            f"- Tổng số tệp tin đã lưu: <b>{total_files}</b>\n"
                                            f"- Tổng dung lượng đã sử dụng: <b>{size_str}</b>\n\n"
                                            f"[Báo cáo thời gian thực từ GramDrive Desktop]"
                                        )
                                        
                                    if reply_text:
                                        reply_url = f"https://api.telegram.org/bot{self.token}/sendMessage"
                                        await session.post(reply_url, json={
                                            "chat_id": chat_id,
                                            "text": reply_text,
                                            "parse_mode": "HTML"
                                        })
            except Exception:
                pass
            await asyncio.sleep(2)
