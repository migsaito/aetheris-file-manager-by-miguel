import os
import sys
import subprocess
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QComboBox, QFrame, QLabel,
    QTreeView, QHeaderView, QMessageBox, QMenu
)
from PyQt6.QtCore import QDir, Qt, QSettings
from PyQt6.QtGui import QFileSystemModel, QAction, QIcon
from aetheris_fm.locales import TRANSLATIONS

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("Aetheris", "FileManagerByMiguel")
        
        # Inicia sempre em en_US por padrão
        saved_lang = self.settings.value("language", "en_US")
        self.current_lang = saved_lang if saved_lang in TRANSLATIONS else "en_US"
        self.history = []
        self.history_index = -1
        
        self.init_ui()
        self.apply_translations()

    def t(self, key):
        return TRANSLATIONS.get(self.current_lang, {}).get(key, key)

    def init_ui(self):
        self.resize(1000, 650)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(6)

        # Aviso Root (Removível)
        is_root = (os.geteuid() == 0)
        show_root_banner = self.settings.value("show_root_banner", "true") == "true"
        
        if is_root and show_root_banner:
            self.root_frame = QFrame()
            self.root_frame.setStyleSheet(
                "background-color: #8b0000; color: #ffffff; border-radius: 4px; padding: 4px;"
            )
            root_layout = QHBoxLayout(self.root_frame)
            root_layout.setContentsMargins(8, 4, 8, 4)
            
            self.root_label = QLabel()
            self.root_label.setStyleSheet("font-weight: bold;")
            
            self.btn_dismiss_root = QPushButton()
            self.btn_dismiss_root.setStyleSheet("background: #500; color: white; border: 1px solid #700; padding: 3px 8px;")
            self.btn_dismiss_root.clicked.connect(self.dismiss_root_warning)
            
            root_layout.addWidget(self.root_label)
            root_layout.addStretch()
            root_layout.addWidget(self.btn_dismiss_root)
            self.main_layout.addWidget(self.root_frame)
        else:
            self.root_frame = None

        # Barra de Navegação
        nav_layout = QHBoxLayout()
        self.btn_back = QPushButton()
        self.btn_back.clicked.connect(self.nav_back)
        self.btn_forward = QPushButton()
        self.btn_forward.clicked.connect(self.nav_forward)
        self.btn_home = QPushButton()
        self.btn_home.clicked.connect(self.nav_home)
        self.btn_refresh = QPushButton()
        self.btn_refresh.clicked.connect(self.nav_refresh)

        self.path_input = QLineEdit()
        self.path_input.returnPressed.connect(self.navigate_to_path)

        # Seletor de Idioma
        self.lang_combo = QComboBox()
        for code, data in TRANSLATIONS.items():
            self.lang_combo.addItem(data["lang_name"], code)
        
        index = self.lang_combo.findData(self.current_lang)
        if index != -1:
            self.lang_combo.setCurrentIndex(index)
        self.lang_combo.currentIndexChanged.connect(self.change_language)

        nav_layout.addWidget(self.btn_back)
        nav_layout.addWidget(self.btn_forward)
        nav_layout.addWidget(self.btn_home)
        nav_layout.addWidget(self.btn_refresh)
        nav_layout.addWidget(self.path_input)
        nav_layout.addWidget(self.lang_combo)
        self.main_layout.addLayout(nav_layout)

        # Visualizador de Arquivos
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        self.model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot | QDir.Filter.Hidden)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setAnimated(True)
        self.tree.setSortingEnabled(True)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.doubleClicked.connect(self.on_item_double_clicked)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.open_context_menu)

        self.main_layout.addWidget(self.tree)

        initial_path = QDir.homePath()
        self.go_to(initial_path)

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

    def apply_translations(self):
        self.setWindowTitle(self.t("title"))
        if self.root_frame:
            self.root_label.setText(self.t("root_warn"))
            self.btn_dismiss_root.setText(self.t("dismiss"))
        self.btn_back.setText(self.t("back"))
        self.btn_forward.setText(self.t("forward"))
        self.btn_home.setText(self.t("home"))
        self.btn_refresh.setText(self.t("refresh"))

    def go_to(self, path, track_history=True):
        if not os.path.exists(path):
            return
        if track_history:
            if self.history_index < len(self.history) - 1:
                self.history = self.history[:self.history_index + 1]
            self.history.append(path)
            self.history_index = len(self.history) - 1
        
        index = self.model.index(path)
        self.tree.setRootIndex(index)
        self.path_input.setText(path)

    def nav_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.go_to(self.history[self.history_index], track_history=False)

    def nav_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.go_to(self.history[self.history_index], track_history=False)

    def nav_home(self):
        self.go_to(QDir.homePath())

    def nav_refresh(self):
        current_path = self.path_input.text()
        self.go_to(current_path, track_history=False)

    def navigate_to_path(self):
        target = self.path_input.text()
        if os.path.isdir(target):
            self.go_to(target)

    def on_item_double_clicked(self, index):
        path = self.model.filePath(index)
        if self.model.isDir(index):
            self.go_to(path)
        else:
            try:
                subprocess.Popen(["xdg-open", path], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to open file: {e}")

    def open_context_menu(self, position):
        index = self.tree.indexAt(position)
        if not index.isValid():
            return
        path = self.model.filePath(index)
        
        menu = QMenu()
        act_open = QAction(self.t("open"), self)
        act_open.triggered.connect(lambda: self.on_item_double_clicked(index))
        menu.addAction(act_open)

        act_delete = QAction(self.t("delete"), self)
        act_delete.triggered.connect(lambda: self.delete_item(path))
        menu.addAction(act_delete)

        menu.exec(self.tree.viewport().mapToGlobal(position))

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
                    os.rmdir(path)
                else:
                    os.remove(path)
                self.nav_refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
