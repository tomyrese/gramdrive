import time
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt
import humanize
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from core.file_manager import FileManager

class SpeedGraphCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=3, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, facecolor='none')
        self.axes = fig.add_subplot(111, facecolor='none')
        super().__init__(fig)
        self.setParent(parent)
        self.setStyleSheet("background-color: transparent;")
        
        self.axes.spines['bottom'].set_color('#33333b')
        self.axes.spines['left'].set_color('#33333b')
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.tick_params(colors='#8e8e93', labelsize=8)
        self.axes.grid(True, color='#1e1e2d', linestyle='--')
        
        self.x_data = list(range(10))
        self.y_data = [0.0] * 10
        self.line, = self.axes.plot(self.x_data, self.y_data, color='#00f2fe', linewidth=2)
        
    def update_data(self, new_val: float):
        self.y_data.pop(0)
        self.y_data.append(new_val / (1024 * 1024))
        self.line.set_ydata(self.y_data)
        self.axes.relim()
        self.axes.autoscale_view()
        self.draw()

from gui.translations import TRANSLATIONS

class DashboardPage(QWidget):
    def __init__(self, file_manager: FileManager, parent=None):
        super().__init__(parent)
        self.file_manager = file_manager
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

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        self.card_files = self.create_card("", "0")
        self.card_size = self.create_card("", "0 Bytes")
        self.card_speed = self.create_card("", "0.00 MB/s")

        self.lbl_card_files_title = self.card_files.findChildren(QLabel)[0]
        self.lbl_card_size_title = self.card_size.findChildren(QLabel)[0]
        self.lbl_card_speed_title = self.card_speed.findChildren(QLabel)[0]

        cards_layout.addWidget(self.card_files)
        cards_layout.addWidget(self.card_size)
        cards_layout.addWidget(self.card_speed)
        layout.addLayout(cards_layout)

        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(20)

        graph_frame = QFrame()
        graph_frame.setObjectName("card")
        graph_layout = QVBoxLayout(graph_frame)
        self.graph_title_lbl = QLabel()
        self.graph_title_lbl.setStyleSheet("font-weight: 600; font-size: 14px; color: #ffffff;")
        graph_layout.addWidget(self.graph_title_lbl)
        
        self.canvas = SpeedGraphCanvas(self, width=5, height=2.5)
        graph_layout.addWidget(self.canvas)
        mid_layout.addWidget(graph_frame, 3)

        recent_frame = QFrame()
        recent_frame.setObjectName("card")
        recent_layout = QVBoxLayout(recent_frame)
        self.recent_title_lbl = QLabel()
        self.recent_title_lbl.setStyleSheet("font-weight: 600; font-size: 14px; color: #ffffff;")
        recent_layout.addWidget(self.recent_title_lbl)

        self.recent_list = QListWidget()
        self.recent_list.setStyleSheet("background: transparent; border: none;")
        recent_layout.addWidget(self.recent_list)
        mid_layout.addWidget(recent_frame, 2)

        layout.addLayout(mid_layout)
        self.retranslate_ui()
        self.refresh_dashboard()

    def get_text(self, key: str) -> str:
        lang = self.file_manager.db.get_setting("language", "vi")
        return TRANSLATIONS.get(lang, TRANSLATIONS["vi"]).get(key, key)

    def retranslate_ui(self):
        self.title_lbl.setText(self.get_text("dashboard_title"))
        self.subtitle_lbl.setText(self.get_text("dashboard_subtitle"))
        self.lbl_card_files_title.setText(self.get_text("card_files"))
        self.lbl_card_size_title.setText(self.get_text("card_size"))
        self.lbl_card_speed_title.setText(self.get_text("card_speed"))
        self.graph_title_lbl.setText(self.get_text("graph_title"))
        self.recent_title_lbl.setText(self.get_text("recent_files"))

    def create_card(self, title: str, value: str) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #8e8e93; font-size: 12px; font-weight: 500;")
        lbl_val = QLabel(value)
        lbl_val.setStyleSheet("font-size: 20px; font-weight: 700; color: #ffffff; margin-top: 4px;")
        
        card_layout.addWidget(lbl_title)
        card_layout.addWidget(lbl_val)
        return card

    def refresh_dashboard(self):
        stats = self.file_manager.get_storage_usage()
        
        lbl_files = self.card_files.findChildren(QLabel)[1]
        lbl_files.setText(str(stats["total_files"]))

        lbl_size = self.card_size.findChildren(QLabel)[1]
        lbl_size.setText(humanize.naturalsize(stats["total_size"], binary=True))

        all_files = self.file_manager.db.get_all_files()
        
        seen_hashes = set()
        unique_files = []
        for f in all_files:
            h = f["hash"]
            if h not in seen_hashes:
                seen_hashes.add(h)
                unique_files.append(f)

        self.recent_list.clear()
        for f in unique_files[:5]:
            item = QListWidgetItem(f"{f['filename']} ({humanize.naturalsize(f['size'], binary=True)})")
            item.setData(Qt.UserRole, f)
            self.recent_list.addItem(item)

    def update_speed(self, speed_bytes: float):
        lbl_speed = self.card_speed.findChildren(QLabel)[1]
        mb_speed = speed_bytes / (1024 * 1024)
        lbl_speed.setText(f"{mb_speed:.2f} MB/s")
        self.canvas.update_data(speed_bytes)
