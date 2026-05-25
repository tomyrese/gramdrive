import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QPushButton, QStackedWidget, QLabel, QSystemTrayIcon, QMenu, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QAction
from core.file_manager import FileManager
from gui.dashboard_page import DashboardPage
from gui.explorer_page import ExplorerPage
from gui.upload_page import UploadPage
from gui.download_page import DownloadPage
from gui.settings_page import SettingsPage
from gui.translations import TRANSLATIONS

class MainWindow(QMainWindow):
    def __init__(self, file_manager: FileManager):
        super().__init__()
        self.file_manager = file_manager
        self.setWindowTitle("Telegram Drive Manager")
        self.setMinimumSize(1100, 700)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self._drag_position = None
        self.init_ui()
        self.setup_tray()
        self.check_connection()

    def init_ui(self):
        self.setAttribute(Qt.WA_TranslucentBackground)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        outer_layout = QVBoxLayout(central_widget)
        outer_layout.setContentsMargins(10, 10, 10, 10)
        outer_layout.setSpacing(0)

        self.main_frame = QFrame()
        self.main_frame.setObjectName("main_window_frame")
        outer_layout.addWidget(self.main_frame)

        main_layout = QHBoxLayout(self.main_frame)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(230)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(16, 24, 16, 24)
        sidebar_layout.setSpacing(10)

        app_title = QLabel("GramDrive")
        app_title.setObjectName("app_title")
        sidebar_layout.addWidget(app_title)

        self.nav_buttons = []
        
        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_dashboard.setCheckable(True)
        self.btn_dashboard.setChecked(True)
        self.btn_dashboard.setObjectName("nav_btn")
        self.btn_dashboard.clicked.connect(lambda: self.switch_page(0))
        sidebar_layout.addWidget(self.btn_dashboard)
        self.nav_buttons.append(self.btn_dashboard)

        self.btn_explorer = QPushButton("File Explorer")
        self.btn_explorer.setCheckable(True)
        self.btn_explorer.setObjectName("nav_btn")
        self.btn_explorer.clicked.connect(lambda: self.switch_page(1))
        sidebar_layout.addWidget(self.btn_explorer)
        self.nav_buttons.append(self.btn_explorer)

        self.btn_upload = QPushButton("Upload Center")
        self.btn_upload.setCheckable(True)
        self.btn_upload.setObjectName("nav_btn")
        self.btn_upload.clicked.connect(lambda: self.switch_page(2))
        sidebar_layout.addWidget(self.btn_upload)
        self.nav_buttons.append(self.btn_upload)

        self.btn_download = QPushButton("Downloads")
        self.btn_download.setCheckable(True)
        self.btn_download.setObjectName("nav_btn")
        self.btn_download.clicked.connect(lambda: self.switch_page(3))
        sidebar_layout.addWidget(self.btn_download)
        self.nav_buttons.append(self.btn_download)

        self.btn_settings = QPushButton("Settings")
        self.btn_settings.setCheckable(True)
        self.btn_settings.setObjectName("nav_btn")
        self.btn_settings.clicked.connect(lambda: self.switch_page(4))
        sidebar_layout.addWidget(self.btn_settings)
        self.nav_buttons.append(self.btn_settings)

        sidebar_layout.addStretch()

        self.btn_exit_app = QPushButton("Exit")
        self.btn_exit_app.setObjectName("nav_btn")
        self.btn_exit_app.clicked.connect(self.close_completely)
        sidebar_layout.addWidget(self.btn_exit_app)

        self.conn_label = QLabel("Connection: Checking...")
        self.conn_label.setStyleSheet("color: #8e8e93; font-size: 11px;")
        sidebar_layout.addWidget(self.conn_label)

        main_layout.addWidget(self.sidebar)

        self.content_container = QFrame()
        self.content_container.setObjectName("main_container")
        
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stacked_widget = QStackedWidget()
        
        self.dashboard_page = DashboardPage(self.file_manager, self)
        self.explorer_page = ExplorerPage(self.file_manager, self.trigger_download_action, self)
        self.upload_page = UploadPage(self.file_manager, self.dashboard_page.update_speed, self)
        self.download_page = DownloadPage(self.file_manager, self.dashboard_page.update_speed, self)
        self.settings_page = SettingsPage(self.file_manager, self.reload_client, self)

        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.explorer_page)
        self.stacked_widget.addWidget(self.upload_page)
        self.stacked_widget.addWidget(self.download_page)
        self.stacked_widget.addWidget(self.settings_page)

        content_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(self.content_container)

        self.load_stylesheet()
        self.retranslate_ui()

    def load_stylesheet(self):
        theme = self.file_manager.db.get_setting("theme", "dark")
        active_theme = theme
        if theme == "system":
            import winreg
            try:
                registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                active_theme = "light" if value == 1 else "dark"
            except Exception:
                active_theme = "dark"
        
        qss_path = f"config/themes/{active_theme}_glass.qss"
        if os.path.exists(qss_path):
            with open(qss_path, "r") as f:
                self.setStyleSheet(f.read())

    def switch_page(self, index: int):
        self.stacked_widget.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        if index == 0:
            self.dashboard_page.refresh_dashboard()
        elif index == 1:
            self.explorer_page.refresh_table()

    def reload_client(self):
        db = self.file_manager.db
        token = db.get_setting("bot_token", "")
        chat_id = db.get_setting("chat_id", "")
        
        self.file_manager.client.token = token
        self.file_manager.client.chat_id = chat_id
        self.file_manager.client.api_url = f"https://api.telegram.org/bot{token}"
        self.file_manager.client.file_url = f"https://api.telegram.org/file/bot{token}"
        
        self.check_connection()
        self.load_stylesheet()
        self.retranslate_ui()

    def get_text(self, key: str) -> str:
        lang = self.file_manager.db.get_setting("language", "vi")
        return TRANSLATIONS.get(lang, TRANSLATIONS["vi"]).get(key, key)

    def retranslate_ui(self):
        self.btn_dashboard.setText(self.get_text("nav_dashboard"))
        self.btn_explorer.setText(self.get_text("nav_explorer"))
        self.btn_upload.setText(self.get_text("nav_upload"))
        self.btn_download.setText(self.get_text("nav_download"))
        self.btn_settings.setText(self.get_text("nav_settings"))
        self.btn_exit_app.setText(self.get_text("nav_exit"))
        if hasattr(self, "dashboard_page"):
            self.dashboard_page.retranslate_ui()
        if hasattr(self, "explorer_page"):
            self.explorer_page.retranslate_ui()
        if hasattr(self, "upload_page"):
            self.upload_page.retranslate_ui()
        if hasattr(self, "download_page"):
            self.download_page.retranslate_ui()
        if hasattr(self, "settings_page"):
            self.settings_page.retranslate_ui()
        self.check_connection()

    def check_connection(self):
        async def run_check():
            connected = await self.file_manager.client.test_connection()
            if connected:
                self.conn_label.setText(self.get_text("conn_active"))
                self.conn_label.setStyleSheet("color: #34c759; font-size: 11px;")
            else:
                self.conn_label.setText(self.get_text("conn_offline"))
                self.conn_label.setStyleSheet("color: #ff3b30; font-size: 11px;")
        
        import asyncio
        asyncio.create_task(run_check())

    def trigger_download_action(self, filename: str, file_hash: str, dest_path: str):
        self.download_page.trigger_download(filename, file_hash, dest_path)
        self.switch_page(3)

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        
        icon_path = "gui/assets/logo.png"
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            self.tray_icon.setIcon(QIcon.fromTheme("drive-harddisk"))
            
        tray_menu = QMenu()
        
        show_action = QAction("Show Window", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide Window", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close_completely)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def closeEvent(self, event):
        self.close_completely()

    def close_completely(self):
        self.tray_icon.hide()
        os._exit(0)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_position is not None:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
