import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableView, 
    QHeaderView, QMenu, QFileDialog, QMessageBox, QDialog, QTextEdit
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QAction, QCursor
from PySide6.QtCore import Qt, QSize
import humanize
from core.file_manager import FileManager
from gui.translations import FramelessMessageBox, TRANSLATIONS

class MetadataDialog(QDialog):
    def __init__(self, file_meta: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Metadata - {file_meta.get('filename')}")
        self.setMinimumSize(450, 300)
        self.setStyleSheet("background-color: #1c1c24; color: #ffffff;")
        
        layout = QVBoxLayout(self)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("background-color: #0b0b0f; border: 1px solid rgba(255,255,255,0.1); color: #00f2fe; font-family: Consolas;")
        
        meta_str = ""
        for k, v in file_meta.items():
            meta_str += f"{k}: {v}\n"
        text_edit.setText(meta_str)
        
        layout.addWidget(text_edit)
        
        close_btn = QPushButton("Close")
        close_btn.setObjectName("accent_btn")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

class ExplorerPage(QWidget):
    def __init__(self, file_manager: FileManager, download_trigger, parent=None):
        super().__init__(parent)
        self.file_manager = file_manager
        self.download_trigger = download_trigger
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()
        title_section = QVBoxLayout()
        self.title_lbl = QLabel()
        self.title_lbl.setObjectName("title_label")
        self.subtitle_lbl = QLabel()
        self.subtitle_lbl.setObjectName("subtitle_label")
        title_section.addWidget(self.title_lbl)
        title_section.addWidget(self.subtitle_lbl)
        header_layout.addLayout(title_section)

        btn_layout = QHBoxLayout()
        self.export_btn = QPushButton()
        self.export_btn.clicked.connect(self.export_csv)
        self.import_btn = QPushButton()
        self.import_btn.clicked.connect(self.import_csv)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.import_btn)
        header_layout.addLayout(btn_layout)
        layout.addLayout(header_layout)

        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        self.search_bar = QLineEdit()
        self.search_bar.textChanged.connect(self.filter_files)
        search_layout.addWidget(self.search_bar)
        
        layout.addLayout(search_layout)

        self.table_view = QTableView()
        self.table_view.setFocusPolicy(Qt.NoFocus)
        self.table_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.show_context_menu)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setAlternatingRowColors(False)
        self.table_view.setShowGrid(False)
        
        self.table_view.verticalHeader().setVisible(False)
        
        self.model = QStandardItemModel(0, 7)
        self.table_view.setModel(self.model)
        
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        
        layout.addWidget(self.table_view)

        self.retranslate_ui()
        self.refresh_table()

    def get_text(self, key: str) -> str:
        lang = self.file_manager.db.get_setting("language", "vi")
        return TRANSLATIONS.get(lang, TRANSLATIONS["vi"]).get(key, key)

    def retranslate_ui(self):
        self.title_lbl.setText(self.get_text("explorer_title"))
        self.subtitle_lbl.setText(self.get_text("explorer_subtitle"))
        self.export_btn.setText(self.get_text("btn_export"))
        self.import_btn.setText(self.get_text("btn_import"))
        self.search_bar.setPlaceholderText(self.get_text("search_placeholder"))
        self.model.setHorizontalHeaderLabels([
            self.get_text("table_name"),
            self.get_text("table_size"),
            self.get_text("table_type"),
            self.get_text("table_date"),
            self.get_text("table_chunks"),
            self.get_text("table_encrypted"),
            self.get_text("table_favorite")
        ])

    def refresh_table(self):
        self.model.setRowCount(0)
        query = self.search_bar.text().strip()
        
        if query:
            files = self.file_manager.search_file(query)
        else:
            files = self.file_manager.db.get_all_files()

        seen_hashes = set()
        unique_files = []
        for f in files:
            h = f["hash"]
            if h not in seen_hashes:
                seen_hashes.add(h)
                unique_files.append(f)

        for f in unique_files:
            name_item = QStandardItem(f["filename"])
            name_item.setData(f, Qt.UserRole)
            
            size_item = QStandardItem(humanize.naturalsize(f["size"], binary=True))
            type_item = QStandardItem(f["type"].upper())
            date_item = QStandardItem(f["upload_date"])
            chunks_item = QStandardItem(str(f["total_chunks"]))
            enc_item = QStandardItem("Yes" if f["encrypted"] == 1 else "No")
            fav_item = QStandardItem("★" if f["favorite"] == 1 else "☆")
            
            name_item.setEditable(False)
            size_item.setEditable(False)
            type_item.setEditable(False)
            date_item.setEditable(False)
            chunks_item.setEditable(False)
            enc_item.setEditable(False)
            fav_item.setEditable(False)

            self.model.appendRow([
                name_item, size_item, type_item, date_item, chunks_item, enc_item, fav_item
            ])

    def filter_files(self):
        self.refresh_table()

    def show_context_menu(self, pos):
        index = self.table_view.indexAt(pos)
        if not index.isValid():
            return
        
        row = index.row()
        name_item = self.model.item(row, 0)
        file_meta = name_item.data(Qt.UserRole)
        
        menu = QMenu(self)
        menu.setStyleSheet("background-color: #1c1c24; color: #ffffff;")
        
        download_action = QAction("Download", self)
        download_action.triggered.connect(lambda: self.download_file(file_meta))
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_file(file_meta))
        
        copy_action = QAction("Copy File Hash", self)
        copy_action.triggered.connect(lambda: self.copy_hash(file_meta))
        
        meta_action = QAction("Open Metadata", self)
        meta_action.triggered.connect(lambda: self.open_metadata(file_meta))
        
        fav_label = "Unfavorite" if file_meta["favorite"] == 1 else "Favorite"
        fav_action = QAction(fav_label, self)
        fav_action.triggered.connect(lambda: self.toggle_favorite(file_meta))
        
        menu.addAction(download_action)
        menu.addAction(delete_action)
        menu.addSeparator()
        menu.addAction(copy_action)
        menu.addAction(meta_action)
        menu.addAction(fav_action)
        
        menu.exec_(QCursor.pos())

    def download_file(self, file_meta: dict):
        dest_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", file_meta["filename"]
        )
        if dest_path:
            self.download_trigger(file_meta["filename"], file_meta["hash"], dest_path)

    def delete_file(self, file_meta: dict):
        msg = FramelessMessageBox(
            QMessageBox.Question, 
            "Delete File", 
            f"Are you sure you want to delete {file_meta['filename']}?",
            QMessageBox.Yes | QMessageBox.No,
            self
        )
        def handle_finished(result):
            if result == QMessageBox.Yes:
                async def run_delete():
                    success = await self.file_manager.delete_file(file_meta["id"])
                    if success:
                        self.refresh_table()
                import asyncio
                asyncio.create_task(run_delete())
        msg.finished.connect(handle_finished)
        msg.open()

    def copy_hash(self, file_meta: dict):
        from PySide6.QtGui import QClipboard
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(file_meta["hash"])

    def open_metadata(self, file_meta: dict):
        dialog = MetadataDialog(file_meta, self)
        dialog.exec_()

    def toggle_favorite(self, file_meta: dict):
        new_fav = 0 if file_meta["favorite"] == 1 else 1
        self.file_manager.db.update_favorite(file_meta["id"], new_fav)
        self.refresh_table()

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, self.get_text("msg_export"), "", "CSV Files (*.csv)")
        if path:
            self.file_manager.export_metadata_csv(path)
            msg_text = self.get_text("msg_export_success").format(filename=os.path.basename(path))
            FramelessMessageBox.show_info(self, self.get_text("msg_export"), msg_text)

    def import_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, self.get_text("msg_import"), "", "CSV Files (*.csv)")
        if path:
            self.file_manager.import_metadata_csv(path)
            self.refresh_table()
            FramelessMessageBox.show_info(self, self.get_text("msg_import"), self.get_text("msg_import_success"))
