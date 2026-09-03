import os
import sys
import time
import shutil
import subprocess
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QComboBox, QFrame, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QMenu, QAbstractItemView
)
from PyQt6.QtCore import Qt, QSettings, QByteArray
from PyQt6.QtGui import QAction, QIcon, QPixmap, QPainter, QColor
from PyQt6.QtSvg import QSvgRenderer
from aetheris_fm.locales import TRANSLATIONS

SVG_FOLDER = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#8caaee"><path d="M10 4H4c-1.11 0-2 .89-2 2v12c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2h-8l-2-2z"/></svg>"""
SVG_FILE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#babbf1"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>"""

def render_svg_icon(svg_str, size=24):
    renderer = QSvgRenderer(QByteArray(svg_str.encode('utf-8')))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)

STANDALONE_STYLE = """
QMainWindow {
    background-color: #1e1e2e;
}

QWidget {
    color: #cdd6f4;
    font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
    font-size: 14px;
}

QLineEdit {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 8px 14px;
    color: #cdd6f4;
    selection-background-color: #89b4fa;
    selection-color: #1e1e2e;
}

QLineEdit:focus {
    border: 1px solid #89b4fa;
}

QPushButton {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 8px 16px;
    color: #cdd6f4;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #45475a;
    border-color: #585b70;
}

QPushButton:pressed {
    background-color: #585b70;
}

QComboBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 6px 14px;
    color: #cdd6f4;
    font-weight: 500;
    min-width: 140px;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 8px;
    selection-background-color: #89b4fa;
    selection-color: #1e1e2e;
    color: #cdd6f4;
    outline: none;
}

QTableWidget {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 12px;
    gridline-color: transparent;
    outline: none;
}

QTableWidget::item {
    height: 38px;
    padding-left: 8px;
    border: none;
    border-bottom: 1px solid #1e1e2e;
}

QTableWidget::item:hover {
    background-color: #313244;
}

QTableWidget::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}

QHeaderView::section {
    background-color: #11111b;
    color: #a6adc8;
    padding: 12px 14px;
    border: none;
    border-bottom: 2px solid #313244;
    font-weight: 700;
    font-size: 13px;
    text-transform: uppercase;
}

QMenu {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 6px;
}

QMenu::item {
    padding: 8px 28px 8px 16px;
    border-radius: 6px;
}

QMenu::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}

QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 12px;
    margin: 4px;
}

QScrollBar::handle:vertical {
    background: #45475a;
    min-height: 24px;
    border-radius: 6px;
}

QScrollBar::handle:vertical:hover {
    background: #585b70;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("Aetheris", "FileManagerByMiguel")
        self.current_lang = "en_US"
        self.current_path = os.path.expanduser("~")
        self.history = []
        self.history_index = -1
        self.icon_folder = render_svg_icon(SVG_FOLDER)
        self.icon_file = render_svg_icon(SVG_FILE)
        self.setStyleSheet(STANDALONE_STYLE)
        self.init_ui()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logo.png")
        if not os.path.exists(icon_path):
            icon_path = "/usr/share/pixmaps/aetheris-file-manager-by-miguel.png"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.apply_translations()
        self.go_to(self.current_path)

    def t(self, key):
        return TRANSLATIONS.get(self.current_lang, {}).get(key, key)

    def init_ui(self):
        self.resize(1100, 720)
        self.setMinimumSize(800, 500)
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(14, 14, 14, 14)
        self.main_layout.setSpacing(12)
        is_root = (os.geteuid() == 0)
        show_root_banner = self.settings.value("show_root_banner", "true") == "true"
        
        if is_root and show_root_banner:
            self.root_frame = QFrame()
            self.root_frame.setStyleSheet(
                "background-color: #f38ba8; color: #11111b; border-radius: 8px; padding: 8px;"
            )
            root_layout = QHBoxLayout(self.root_frame)
            root_layout.setContentsMargins(12, 4, 12, 4)
            self.root_label = QLabel()
            self.root_label.setStyleSheet("font-weight: 800; background: transparent; border: none;")
            self.btn_dismiss_root = QPushButton()
            self.btn_dismiss_root.setStyleSheet(
                "background: #11111b; color: #f38ba8; border: none; padding: 6px 14px; border-radius: 6px;"
            )
            self.btn_dismiss_root.clicked.connect(self.dismiss_root_warning)
            root_layout.addWidget(self.root_label)
            root_layout.addStretch()
            root_layout.addWidget(self.btn_dismiss_root)
            self.main_layout.addWidget(self.root_frame)
        else:
            self.root_frame = None

        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(8)
        self.btn_back = QPushButton("◀")
        self.btn_back.setFixedWidth(44)
        self.btn_back.clicked.connect(self.nav_back)
        self.btn_forward = QPushButton("▶")
        self.btn_forward.setFixedWidth(44)
        self.btn_forward.clicked.connect(self.nav_forward)
        self.btn_home = QPushButton()
        self.btn_home.clicked.connect(self.nav_home)
        self.btn_refresh = QPushButton()
        self.btn_refresh.clicked.connect(self.nav_refresh)
        self.path_input = QLineEdit()
        self.path_input.returnPressed.connect(self.navigate_to_path)
        self.lang_combo = QComboBox()
        for code, data in TRANSLATIONS.items():
            self.lang_combo.addItem(data["lang_name"], code)
        idx = self.lang_combo.findData("en_US")
        if idx != -1:
            self.lang_combo.setCurrentIndex(idx)
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        nav_layout.addWidget(self.btn_back)
        nav_layout.addWidget(self.btn_forward)
        nav_layout.addWidget(self.btn_home)
        nav_layout.addWidget(self.btn_refresh)
        nav_layout.addWidget(self.path_input)
        nav_layout.addWidget(self.lang_combo)
        self.main_layout.addLayout(nav_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.cellDoubleClicked.connect(self.on_row_double_clicked)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.open_context_menu)
        self.main_layout.addWidget(self.table)

    def dismiss_root_warning(self):
        if self.root_frame:
            self.root_frame.setVisible(False)
            self.settings.setValue("show_root_banner", "false")

    def change_language(self):
        new_lang = self.lang_combo.currentData()
        if new_lang:
            self.current_lang = new_lang
            self.settings.setValue("language", new_lang)
            self.apply_translations()
            self.load_directory(self.current_path)

    def apply_translations(self):
        self.setWindowTitle(self.t("title"))
        if self.root_frame:
            self.root_label.setText(self.t("root_warn"))
            self.btn_dismiss_root.setText(self.t("dismiss"))
        self.btn_home.setText(self.t("home"))
        self.btn_refresh.setText(self.t("refresh"))
        self.table.setHorizontalHeaderLabels([
            self.t("col_name"),
            self.t("col_size"),
            self.t("col_type"),
            self.t("col_date")
        ])

    def format_size(self, size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    def load_directory(self, path):
        if not os.path.isdir(path):
            return
        self.current_path = os.path.abspath(path)
        self.path_input.setText(self.current_path)
        self.table.setRowCount(0)
        try:
            entries = os.scandir(self.current_path)
        except PermissionError:
            QMessageBox.critical(self, "Error", f"Permission denied:\n{self.current_path}")
            return
        dirs, files = [], []
        for entry in entries:
            try:
                stat = entry.stat(follow_symlinks=False)
                info = (entry.name, entry.is_dir(follow_symlinks=False), stat.st_size, stat.st_mtime)
                if info[1]:
                    dirs.append(info)
                else:
                    files.append(info)
            except Exception:
                continue
        dirs.sort(key=lambda x: x[0].lower())
        files.sort(key=lambda x: x[0].lower())
        all_items = dirs + files
        self.table.setRowCount(len(all_items))
        for row, (name, is_dir, size, mtime) in enumerate(all_items):
            item_name = QTableWidgetItem(name)
            item_name.setIcon(self.icon_folder if is_dir else self.icon_file)
            item_name.setData(Qt.ItemDataRole.UserRole, os.path.join(self.current_path, name))
            item_name.setData(Qt.ItemDataRole.UserRole + 1, is_dir)
            size_str = "" if is_dir else self.format_size(size)
            item_size = QTableWidgetItem(size_str)
            item_size.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            type_str = self.t("type_folder") if is_dir else self.t("type_file")
            item_type = QTableWidgetItem(type_str)
            date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(mtime))
            item_date = QTableWidgetItem(date_str)
            self.table.setItem(row, 0, item_name)
            self.table.setItem(row, 1, item_size)
            self.table.setItem(row, 2, item_type)
            self.table.setItem(row, 3, item_date)

    def go_to(self, path, track_history=True):
        if not os.path.exists(path):
            return
        if track_history:
            if self.history_index < len(self.history) - 1:
                self.history = self.history[:self.history_index + 1]
            self.history.append(path)
            self.history_index = len(self.history) - 1
        self.load_directory(path)

    def nav_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.go_to(self.history[self.history_index], track_history=False)

    def nav_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.go_to(self.history[self.history_index], track_history=False)

    def nav_home(self):
        self.go_to(os.path.expanduser("~"))

    def nav_refresh(self):
        self.load_directory(self.current_path)

    def navigate_to_path(self):
        target = self.path_input.text()
        if os.path.isdir(target):
            self.go_to(target)

    def on_row_double_clicked(self, row, col):
        item = self.table.item(row, 0)
        if not item:
            return
        path = item.data(Qt.ItemDataRole.UserRole)
        is_dir = item.data(Qt.ItemDataRole.UserRole + 1)
        if is_dir:
            self.go_to(path)
        else:
            self.open_file_autonomously(path)

    def open_file_autonomously(self, path):
        try:
            if shutil.which("xdg-open"):
                subprocess.Popen(["xdg-open", path], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                return
            for opener in ["gio", "mimeo", "handlr"]:
                if shutil.which(opener):
                    subprocess.Popen([opener, "open", path], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                    return
            QMessageBox.warning(self, "Aetheris", f"No default opener found for:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file: {e}")

    def open_context_menu(self, position):
        item = self.table.itemAt(position)
        if not item:
            return
        row = item.row()
        target_item = self.table.item(row, 0)
        path = target_item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu(self)
        act_open = QAction(self.t("open"), self)
        act_open.triggered.connect(lambda: self.on_row_double_clicked(row, 0))
        menu.addAction(act_open)
        act_delete = QAction(self.t("delete"), self)
        act_delete.triggered.connect(lambda: self.delete_item(path))
        menu.addAction(act_delete)
        menu.exec(self.table.viewport().mapToGlobal(position))

    def delete_item(self, path):
        reply = QMessageBox.question(
            self,
            self.t("delete"),
            f"{self.t('confirm_del')}\n{path}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self.nav_refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
