import os
import sys
import asyncio
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QPainter, QLinearGradient, QColor, QFont
from qasync import QEventLoop

from core.database import Database
from core.telegram_client import TelegramClient
from core.uploader import Uploader
from core.downloader import Downloader
from core.cache_manager import CacheManager
from core.file_manager import FileManager
from gui.main_window import MainWindow

def create_splash_pixmap() -> QPixmap:
    pixmap = QPixmap(500, 300)
    pixmap.fill(Qt.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    gradient = QLinearGradient(0, 0, 500, 300)
    gradient.setColorAt(0.0, QColor("#1e1e2d"))
    gradient.setColorAt(1.0, QColor("#0b0b0f"))
    
    painter.setBrush(gradient)
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(0, 0, 500, 300, 16, 16)
    
    painter.setPen(QColor("rgba(255, 255, 255, 0.1)"))
    painter.drawRoundedRect(1, 1, 498, 298, 16, 16)
    
    font_title = QFont("Segoe UI", 28, QFont.Bold)
    painter.setFont(font_title)
    painter.setPen(QColor("#ffffff"))
    painter.drawText(0, 0, 500, 180, Qt.AlignCenter, "GramDrive")
    
    font_sub = QFont("Segoe UI", 12)
    painter.setFont(font_sub)
    painter.setPen(QColor("#8e8e93"))
    painter.drawText(0, 80, 500, 180, Qt.AlignCenter, "Telegram Drive Manager")
    
    font_ver = QFont("Segoe UI", 10)
    painter.setFont(font_ver)
    painter.setPen(QColor("#55555d"))
    painter.drawText(20, 260, 460, 30, Qt.AlignLeft, "v1.0.1 (Stable)")
    painter.drawText(20, 260, 460, 30, Qt.AlignRight, "Python 3.11.9 & PySide6")
    
    painter.end()
    return pixmap

async def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    splash_pix = create_splash_pixmap()
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setAttribute(Qt.WA_TranslucentBackground)
    splash.show()
    
    app.processEvents()

    for folder in ["database", "temp", "logs"]:
        os.makedirs(folder, exist_ok=True)

    db = Database()
    cache_mgr = CacheManager()
    cache_mgr.clean_temp_dirs()

    token = db.get_setting("bot_token", "")
    chat_id = db.get_setting("chat_id", "")
    
    client = TelegramClient(token, chat_id)
    uploader = Uploader(db, client)
    downloader = Downloader(db, client)
    file_mgr = FileManager(db, client, uploader, downloader)

    await asyncio.sleep(1.5)

    window = MainWindow(file_mgr)
    
    splash.finish(window)
    window.show()

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    asyncio.run(main())
