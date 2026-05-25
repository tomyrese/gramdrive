import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QListWidget, QListWidgetItem, QProgressBar, QFrame
)
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDragEnterEvent, QDropEvent
import humanize
from core.file_manager import FileManager

from gui.translations import TRANSLATIONS

class DropZone(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setAcceptDrops(True)
        self.setMinimumHeight(180)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        self.label = QLabel()
        self.label.setStyleSheet("font-size: 16px; font-weight: 600; color: #8e8e93;")
        layout.addWidget(self.label)
        
        self.sub_label = QLabel()
        self.sub_label.setStyleSheet("font-size: 12px; color: #55555d; margin-top: 4px;")
        layout.addWidget(self.sub_label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("background-color: rgba(0, 122, 255, 0.08); border-color: #007aff;")

    def dragLeaveEvent(self, event):
        self.setStyleSheet("")

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet("")
        urls = event.mimeData().urls()
        if urls:
            paths = [url.toLocalFile() for url in urls if os.path.exists(url.toLocalFile())]
            if hasattr(self.parent(), "add_files_to_queue"):
                self.parent().add_files_to_queue(paths)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if hasattr(self.parent(), "browse_files"):
                self.parent().browse_files()

class UploadPage(QWidget):
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

        self.drop_zone = DropZone(self)
        layout.addWidget(self.drop_zone)

        self.queue_title_lbl = QLabel()
        self.queue_title_lbl.setStyleSheet("font-size: 15px; font-weight: 600; color: #ffffff;")
        layout.addWidget(self.queue_title_lbl)

        self.queue_list = QListWidget()
        self.queue_list.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self.queue_list)

        actions_layout = QHBoxLayout()
        self.cancel_btn = QPushButton()
        self.cancel_btn.clicked.connect(self.cancel_uploads)
        actions_layout.addStretch()
        actions_layout.addWidget(self.cancel_btn)
        layout.addLayout(actions_layout)
        self.retranslate_ui()

    def get_text(self, key: str) -> str:
        lang = self.file_manager.db.get_setting("language", "vi")
        return TRANSLATIONS.get(lang, TRANSLATIONS["vi"]).get(key, key)

    def retranslate_ui(self):
        self.title_lbl.setText(self.get_text("upload_title"))
        self.subtitle_lbl.setText(self.get_text("upload_subtitle"))
        self.drop_zone.label.setText(self.get_text("drop_primary"))
        self.drop_zone.sub_label.setText(self.get_text("drop_secondary"))
        self.queue_title_lbl.setText(self.get_text("queue_title"))
        self.cancel_btn.setText(self.get_text("btn_cancel_all"))

    def browse_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Select Files to Upload")
        if paths:
            self.add_files_to_queue(paths)

    def add_files_to_queue(self, paths: list):
        for path in paths:
            if os.path.isdir(path):
                continue
            
            file_id = self.file_manager.upload_file(path)
            
            item = QListWidgetItem()
            widget = QWidget()
            w_layout = QHBoxLayout(widget)
            w_layout.setContentsMargins(8, 8, 8, 8)
            
            lbl_name = QLabel(os.path.basename(path))
            lbl_name.setStyleSheet("font-weight: 500; font-size: 13px; color: #ffffff;")
            
            lbl_size = QLabel(humanize.naturalsize(os.path.getsize(path), binary=True))
            lbl_size.setStyleSheet("color: #8e8e93; font-size: 11px;")
            
            pb = QProgressBar()
            pb.setRange(0, 100)
            pb.setValue(0)
            pb.setMaximumHeight(14)
            
            lbl_status = QLabel("Queued")
            lbl_status.setStyleSheet("color: #8e8e93; font-size: 12px;")
            
            w_layout.addWidget(lbl_name, 2)
            w_layout.addWidget(lbl_size, 1)
            w_layout.addWidget(pb, 3)
            w_layout.addWidget(lbl_status, 1)
            
            item.setSizeHint(widget.sizeHint())
            item.setData(Qt.UserRole, file_id)
            
            self.queue_list.addItem(item)
            self.queue_list.setItemWidget(item, widget)

        import asyncio
        asyncio.create_task(self.start_uploading())

    async def start_uploading(self):
        if self.file_manager.uploader.is_running:
            return
            
        def progress_cb(task):
            for i in range(self.queue_list.count()):
                item = self.queue_list.item(i)
                if item.data(Qt.UserRole) == task.file_id:
                    widget = self.queue_list.itemWidget(item)
                    if widget:
                        pb = widget.findChild(QProgressBar)
                        lbl_status = widget.findChild(QLabel, "")
                        
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
                if item.data(Qt.UserRole) == task.file_id:
                    widget = self.queue_list.itemWidget(item)
                    if widget:
                        labels = widget.findChildren(QLabel)
                        lbl_status = labels[-1]
                        pb = widget.findChild(QProgressBar)
                        
                        if task.status == "Completed":
                            pb.setValue(100)
                            lbl_status.setText("Completed")
                            lbl_status.setStyleSheet("color: #34c759;")
                        else:
                            lbl_status.setText("Failed")
                            lbl_status.setStyleSheet("color: #ff3b30;")
                    break
            self.trigger_speed_update(0.0)

        await self.file_manager.uploader.run_queue(progress_cb, complete_cb)

    def cancel_uploads(self):
        self.file_manager.uploader.cancel_upload()
        self.queue_list.clear()
