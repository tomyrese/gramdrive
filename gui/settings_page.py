from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox, QMessageBox, QFileDialog, QFrame, QScrollArea
)
from PySide6.QtCore import Qt
from core.file_manager import FileManager
from gui.translations import TRANSLATIONS, FramelessMessageBox

class SettingsPage(QWidget):
    def __init__(self, file_manager: FileManager, save_callback, parent=None):
        super().__init__(parent)
        self.file_manager = file_manager
        self.save_callback = save_callback
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setObjectName("settings_scroll")
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll, 1)

        scroll_content = QWidget()
        scroll_content.setObjectName("settings_scroll_content")
        scroll.setWidget(scroll_content)

        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        header_layout = QVBoxLayout()
        self.title_lbl = QLabel()
        self.title_lbl.setObjectName("title_label")
        self.subtitle_lbl = QLabel()
        self.subtitle_lbl.setObjectName("subtitle_label")
        header_layout.addWidget(self.title_lbl)
        header_layout.addWidget(self.subtitle_lbl)
        layout.addLayout(header_layout)

        token_frame = QFrame()
        token_frame.setObjectName("card")
        token_layout = QVBoxLayout(token_frame)
        token_layout.setSpacing(12)
        
        self.token_title_lbl = QLabel()
        self.token_title_lbl.setStyleSheet("font-weight: 600; font-size: 14px; color: #ffffff;")
        token_layout.addWidget(self.token_title_lbl)

        self.token_input = QLineEdit()
        self.lbl_bot_token = QLabel()
        token_layout.addWidget(self.lbl_bot_token)
        token_layout.addWidget(self.token_input)

        self.start_bot_btn = QPushButton()
        self.start_bot_btn.clicked.connect(self.toggle_bot_listener)
        token_layout.addWidget(self.start_bot_btn)

        self.bot_status_lbl = QLabel()
        self.bot_status_lbl.setStyleSheet("color: #ff3b30; font-weight: 500;")
        token_layout.addWidget(self.bot_status_lbl)
        
        layout.addWidget(token_frame)

        chat_frame = QFrame()
        chat_frame.setObjectName("card")
        chat_layout = QVBoxLayout(chat_frame)
        chat_layout.setSpacing(12)

        self.chat_title_lbl = QLabel()
        self.chat_title_lbl.setStyleSheet("font-weight: 600; font-size: 14px; color: #ffffff;")
        chat_layout.addWidget(self.chat_title_lbl)

        self.chat_input = QLineEdit()
        self.lbl_chat_id = QLabel()
        chat_layout.addWidget(self.lbl_chat_id)
        chat_layout.addWidget(self.chat_input)

        self.test_btn = QPushButton()
        self.test_btn.clicked.connect(self.test_connection)
        chat_layout.addWidget(self.test_btn)

        layout.addWidget(chat_frame)

        sec_frame = QFrame()
        sec_frame.setObjectName("card")
        sec_layout = QVBoxLayout(sec_frame)
        sec_layout.setSpacing(12)

        self.sec_title_lbl = QLabel()
        self.sec_title_lbl.setStyleSheet("font-weight: 600; font-size: 14px; color: #ffffff;")
        sec_layout.addWidget(self.sec_title_lbl)

        self.enc_checkbox = QCheckBox()
        sec_layout.addWidget(self.enc_checkbox)

        key_layout = QHBoxLayout()
        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.Password)
        self.btn_toggle_pass = QPushButton("👁️")
        self.btn_toggle_pass.setFixedWidth(40)
        self.btn_toggle_pass.setStyleSheet("padding: 6px;")
        self.btn_toggle_pass.clicked.connect(self.toggle_passphrase_visibility)
        
        key_layout.addWidget(self.key_input)
        key_layout.addWidget(self.btn_toggle_pass)
        
        self.lbl_passphrase = QLabel()
        sec_layout.addWidget(self.lbl_passphrase)
        sec_layout.addLayout(key_layout)

        layout.addWidget(sec_frame)

        limits_frame = QFrame()
        limits_frame.setObjectName("card")
        limits_layout = QVBoxLayout(limits_frame)
        limits_layout.setSpacing(12)

        self.limits_title_lbl = QLabel()
        self.limits_title_lbl.setStyleSheet("font-weight: 600; font-size: 14px; color: #ffffff;")
        limits_layout.addWidget(self.limits_title_lbl)

        self.chunk_combo = QComboBox()
        self.chunk_combo.addItems(["10 MB", "20 MB", "40 MB", "49 MB"])
        self.lbl_chunk_size = QLabel()
        limits_layout.addWidget(self.lbl_chunk_size)
        limits_layout.addWidget(self.chunk_combo)

        layout.addWidget(limits_frame)

        lang_frame = QFrame()
        lang_frame.setObjectName("card")
        lang_layout = QVBoxLayout(lang_frame)
        lang_layout.setSpacing(12)

        self.lang_title_lbl = QLabel()
        self.lang_title_lbl.setStyleSheet("font-weight: 600; font-size: 14px; color: #ffffff;")
        lang_layout.addWidget(self.lang_title_lbl)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Tiếng Việt", "English"])
        self.lbl_language = QLabel()
        lang_layout.addWidget(self.lbl_language)
        lang_layout.addWidget(self.lang_combo)

        layout.addWidget(lang_frame)

        theme_frame = QFrame()
        theme_frame.setObjectName("card")
        theme_layout = QVBoxLayout(theme_frame)
        theme_layout.setSpacing(12)

        self.theme_title_lbl = QLabel()
        self.theme_title_lbl.setStyleSheet("font-weight: 600; font-size: 14px; color: #ffffff;")
        theme_layout.addWidget(self.theme_title_lbl)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark Mode / Giao diện tối", "Light Mode / Giao diện sáng", "System Default / Hệ thống"])
        self.lbl_theme = QLabel()
        theme_layout.addWidget(self.lbl_theme)
        theme_layout.addWidget(self.theme_combo)

        layout.addWidget(theme_frame)

        db_frame = QFrame()
        db_frame.setObjectName("card")
        db_layout = QHBoxLayout(db_frame)
        
        self.backup_btn = QPushButton()
        self.backup_btn.clicked.connect(self.backup_db)
        
        self.restore_btn = QPushButton()
        self.restore_btn.clicked.connect(self.restore_db)

        db_layout.addWidget(self.backup_btn)
        db_layout.addWidget(self.restore_btn)
        
        layout.addWidget(db_frame)
        layout.addStretch()

        self.save_bar = QWidget()
        self.save_bar.setObjectName("settings_save_bar")
        self.save_bar.setStyleSheet("""
            QWidget#settings_save_bar {
                background: transparent;
                border-top: 1px solid rgba(255, 255, 255, 0.05);
            }
        """)
        
        save_layout = QHBoxLayout(self.save_bar)
        save_layout.setContentsMargins(24, 16, 24, 24)
        
        self.save_btn = QPushButton()
        self.save_btn.setObjectName("accent_btn")
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setMinimumWidth(150)
        
        save_layout.addStretch()
        save_layout.addWidget(self.save_btn)
        
        main_layout.addWidget(self.save_bar)

    def get_text(self, key: str) -> str:
        lang = self.file_manager.db.get_setting("language", "vi")
        return TRANSLATIONS.get(lang, TRANSLATIONS["vi"]).get(key, key)

    def retranslate_ui(self):
        self.title_lbl.setText(self.get_text("settings_title"))
        self.subtitle_lbl.setText(self.get_text("settings_subtitle"))
        
        self.token_title_lbl.setText(self.get_text("tg_token_title"))
        self.lbl_bot_token.setText(self.get_text("lbl_bot_token"))
        self.token_input.setPlaceholderText(self.get_text("lbl_bot_token"))
        
        self.chat_title_lbl.setText(self.get_text("tg_chat_title"))
        self.lbl_chat_id.setText(self.get_text("lbl_chat_id"))
        self.chat_input.setPlaceholderText(self.get_text("lbl_chat_id"))
        self.test_btn.setText(self.get_text("btn_test_conn"))
        
        self.sec_title_lbl.setText(self.get_text("sec_title"))
        self.enc_checkbox.setText(self.get_text("cb_encrypt"))
        self.lbl_passphrase.setText(self.get_text("lbl_passphrase"))
        self.key_input.setPlaceholderText(self.get_text("lbl_passphrase"))
        
        self.limits_title_lbl.setText(self.get_text("limits_title"))
        self.lbl_chunk_size.setText(self.get_text("lbl_chunk_size"))
        
        self.lang_title_lbl.setText(self.get_text("lang_title"))
        self.lbl_language.setText(self.get_text("lbl_language"))
        
        self.theme_title_lbl.setText(self.get_text("theme_title") or "Theme / Giao diện")
        self.lbl_theme.setText(self.get_text("lbl_theme") or "Select Theme / Lựa chọn giao diện")
        
        self.backup_btn.setText(self.get_text("btn_backup"))
        self.restore_btn.setText(self.get_text("btn_restore"))
        self.save_btn.setText(self.get_text("btn_save"))
        
        client = self.file_manager.client
        if client.polling_active:
            self.start_bot_btn.setText(self.get_text("btn_stop_bot"))
            self.bot_status_lbl.setText(self.get_text("bot_status_active"))
            self.bot_status_lbl.setStyleSheet("color: #34c759; font-weight: 500;")
        else:
            self.start_bot_btn.setText(self.get_text("btn_start_bot"))
            self.bot_status_lbl.setText(self.get_text("bot_status_inactive"))
            self.bot_status_lbl.setStyleSheet("color: #ff3b30; font-weight: 500;")

    def load_settings(self):
        db = self.file_manager.db
        self.token_input.setText(db.get_setting("bot_token", ""))
        self.chat_input.setText(db.get_setting("chat_id", ""))
        self.enc_checkbox.setChecked(db.get_setting("encryption_enabled", "0") == "1")
        self.key_input.setText(db.get_setting("encryption_key", ""))
        
        chunk_size = int(db.get_setting("chunk_size", str(40 * 1024 * 1024)))
        mb = chunk_size // (1024 * 1024)
        if mb == 10:
            self.chunk_combo.setCurrentIndex(0)
        elif mb == 20:
            self.chunk_combo.setCurrentIndex(1)
        elif mb == 40:
            self.chunk_combo.setCurrentIndex(2)
        elif mb == 49:
            self.chunk_combo.setCurrentIndex(3)

        lang = db.get_setting("language", "vi")
        self.lang_combo.setCurrentIndex(0 if lang == "vi" else 1)

        theme = db.get_setting("theme", "dark")
        if theme == "dark":
            self.theme_combo.setCurrentIndex(0)
        elif theme == "light":
            self.theme_combo.setCurrentIndex(1)
        elif theme == "system":
            self.theme_combo.setCurrentIndex(2)

        self.retranslate_ui()

    def toggle_bot_listener(self):
        db = self.file_manager.db
        token = self.token_input.text().strip()
        if not token:
            FramelessMessageBox.show_warning(self, "Bot Listener", "Please enter a Bot Token first.")
            return

        client = self.file_manager.client
        if client.polling_active:
            client.polling_active = False
            self.save_callback()
        else:
            db.save_setting("bot_token", token)
            client.token = token
            client.api_url = f"https://api.telegram.org/bot{token}"
            client.file_url = f"https://api.telegram.org/file/bot{token}"
            client.polling_active = True

            import asyncio
            asyncio.create_task(client.start_polling())
            self.save_callback()

    def save_settings(self):
        db = self.file_manager.db
        db.save_setting("bot_token", self.token_input.text().strip())
        db.save_setting("chat_id", self.chat_input.text().strip())
        db.save_setting("encryption_enabled", "1" if self.enc_checkbox.isChecked() else "0")
        db.save_setting("encryption_key", self.key_input.text().strip())

        mb_choices = [10, 20, 40, 49]
        mb = mb_choices[self.chunk_combo.currentIndex()]
        db.save_setting("chunk_size", str(mb * 1024 * 1024))

        db.save_setting("language", "vi" if self.lang_combo.currentIndex() == 0 else "en")

        theme_choices = ["dark", "light", "system"]
        theme_val = theme_choices[self.theme_combo.currentIndex()]
        db.save_setting("theme", theme_val)

        self.save_callback()
        FramelessMessageBox.show_info(self, "Settings", "Settings saved successfully")

    def test_connection(self):
        token = self.token_input.text().strip()
        chat_id = self.chat_input.text().strip()
        if not token or not chat_id:
            FramelessMessageBox.show_warning(self, "Test Connection", "Please fill in Token and Chat ID first.")
            return

        async def run_test():
            from core.telegram_client import TelegramClient
            client = TelegramClient(token, chat_id)
            connected = await client.test_connection()
            def show_result():
                if connected:
                    db = self.file_manager.db
                    db.save_setting("bot_token", token)
                    db.save_setting("chat_id", chat_id)
                    self.save_callback()
                    FramelessMessageBox.show_info(self, "Test Connection", "Connection Successful! The bot is active.")
                else:
                    FramelessMessageBox.show_critical(self, "Test Connection", "Connection Failed. Check your Token or Internet connection.")
            show_result()

        import asyncio
        asyncio.create_task(run_test())

    def backup_db(self):
        path, _ = QFileDialog.getSaveFileName(self, "Backup Database", "", "SQLite Database (*.db)")
        if path:
            self.file_manager.db.backup_database(path)
            FramelessMessageBox.show_info(self, "Backup", "Database backup completed successfully")

    def restore_db(self):
        path, _ = QFileDialog.getOpenFileName(self, "Restore Database", "", "SQLite Database (*.db)")
        if path:
            self.file_manager.db.restore_database(path)
            self.load_settings()
            self.save_callback()
            FramelessMessageBox.show_info(self, "Restore", "Database restored successfully. Settings reloaded.")

    def toggle_passphrase_visibility(self):
        if self.key_input.echoMode() == QLineEdit.Password:
            self.key_input.setEchoMode(QLineEdit.Normal)
            self.btn_toggle_pass.setText("🔒")
        else:
            self.key_input.setEchoMode(QLineEdit.Password)
            self.btn_toggle_pass.setText("👁️")
