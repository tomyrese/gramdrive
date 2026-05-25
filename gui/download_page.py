import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QProgressBar
)
from PySide6.QtCore import Qt
import humanize
from core.file_manager import FileManager

from gui.translations import TRANSLATIONS

class DownloadPage(QWidget):
    def __init__(self, file_manager: FileManager, trigger_speed_update, parent=None):
        super().__init__(parent)
        self.file_manager = file_manager
        self.trigger_speed_update = trigger_speed_update
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
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

        self.queue_title_lbl = QLabel()
        self.queue_title_lbl.setStyleSheet("font-size: 15px; font-weight: 600; color: #ffffff;")
        layout.addWidget(self.queue_title_lbl)

        self.queue_list = QListWidget()
        self.queue_list.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self.queue_list)

        actions_layout = QHBoxLayout()
        self.cancel_btn = QPushButton()
        self.cancel_btn.clicked.connect(self.cancel_downloads)
        actions_layout.addStretch()
        actions_layout.addWidget(self.cancel_btn)
        layout.addLayout(actions_layout)
        self.retranslate_ui()

    def get_text(self, key: str) -> str:
        lang = self.file_manager.db.get_setting("language", "vi")
        return TRANSLATIONS.get(lang, TRANSLATIONS["vi"]).get(key, key)

    def retranslate_ui(self):
        self.title_lbl.setText(self.get_text("download_title"))
        self.subtitle_lbl.setText(self.get_text("download_subtitle"))
        self.queue_title_lbl.setText(self.get_text("download_queue"))
        self.cancel_btn.setText(self.get_text("btn_cancel_all"))

    def trigger_download(self, filename: str, file_hash: str, dest_path: str):
        self.file_manager.download_file(filename, file_hash, dest_path)
        
        item = QListWidgetItem()
        widget = QWidget()
        w_layout = QHBoxLayout(widget)
        w_layout.setContentsMargins(8, 8, 8, 8)
        
        lbl_name = QLabel(filename)
        lbl_name.setStyleSheet("font-weight: 500; font-size: 13px; color: #ffffff;")
        
        lbl_dest = QLabel(os.path.basename(dest_path))
        lbl_dest.setStyleSheet("color: #8e8e93; font-size: 11px;")
        
        pb = QProgressBar()
        pb.setRange(0, 100)
        pb.setValue(0)
        pb.setMaximumHeight(14)
        
        lbl_status = QLabel("Queued")
        lbl_status.setStyleSheet("color: #8e8e93; font-size: 12px;")
        
        btn_open = QPushButton("Open")
        btn_open.setStyleSheet("background-color: #34c759; color: #ffffff; padding: 4px 10px; font-size: 11px; border: none; border-radius: 6px; font-weight: 600;")
        btn_open.setVisible(False)
        
        btn_show = QPushButton("Open in Explorer")
        btn_show.setStyleSheet("background-color: #007acc; color: #ffffff; padding: 4px 10px; font-size: 11px; border: none; border-radius: 6px; font-weight: 600;")
        btn_show.setVisible(False)
        
        import subprocess
        btn_open.clicked.connect(lambda: os.startfile(dest_path))
        btn_show.clicked.connect(lambda: subprocess.Popen(f'explorer /select,"{os.path.normpath(dest_path)}"'))
        
        w_layout.addWidget(lbl_name, 2)
        w_layout.addWidget(lbl_dest, 1)
        w_layout.addWidget(pb, 3)
        w_layout.addWidget(lbl_status, 1)
        w_layout.addWidget(btn_open)
        w_layout.addWidget(btn_show)
        
        item.setSizeHint(widget.sizeHint())
        item.setData(Qt.UserRole, file_hash)
        
        self.queue_list.addItem(item)
        self.queue_list.setItemWidget(item, widget)

        import asyncio
        asyncio.create_task(self.start_downloading())

    async def start_downloading(self):
        if self.file_manager.downloader.is_running:
            return
            
        def progress_cb(task):
            for i in range(self.queue_list.count()):
                item = self.queue_list.item(i)
                if item.data(Qt.UserRole) == task.file_hash:
                    widget = self.queue_list.itemWidget(item)
                    if widget:
                        pb = widget.findChild(QProgressBar)
                        labels = widget.findChildren(QLabel)
                        lbl_status = labels[-1]
                        
                        pb.setValue(task.progress)
                        mb_speed = task.speed / (1024 * 1024)
                        lbl_status.setText(f"{task.status} ({mb_speed:.2f} MB/s)")
                        self.trigger_speed_update(task.speed)
                        break

        def complete_cb(task):
            for i in range(self.queue_list.count()):
                item = self.queue_list.item(i)
                if item.data(Qt.UserRole) == task.file_hash:
                    widget = self.queue_list.itemWidget(item)
                    if widget:
                        labels = widget.findChildren(QLabel)
                        lbl_status = labels[-1]
                        pb = widget.findChild(QProgressBar)
                        
                        if task.status == "Completed":
                            pb.setValue(100)
                            lbl_status.setText("Completed")
                            lbl_status.setStyleSheet("color: #34c759;")
                            buttons = widget.findChildren(QPushButton)
                            for btn in buttons:
                                btn.setVisible(True)
                        else:
                            lbl_status.setText("Failed")
                            lbl_status.setStyleSheet("color: #ff3b30;")
                    break
            self.trigger_speed_update(0.0)

        await self.file_manager.downloader.run_queue(progress_cb, complete_cb)

    def cancel_downloads(self):
        self.file_manager.downloader.cancel_download()
        self.queue_list.clear()
