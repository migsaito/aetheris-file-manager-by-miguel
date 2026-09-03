import os
import sys
import subprocess
import shutil
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QComboBox, QFrame, QLabel,
    QTreeView, QHeaderView, QMessageBox, QMenu, QSplitter,
    QListWidget, QListWidgetItem, QStyle
)
from PyQt6.QtCore import QDir, Qt, QSettings, QSize
from PyQt6.QtGui import QFileSystemModel, QAction, QIcon, QFont, QColor, QPalette
from aetheris_fm.locales import TRANSLATIONS

# Folha de estilo independente (Dark / Modern neutro compatível em qualquer DE)
STANDALONE_STYLE = """
QMainWindow {
    background-color: #1e1e24;
}

QWidget {
    color: #e0e0e0;
    font-family: 'Inter', 'Segoe UI', 'Cantarell', 'Ubuntu', sans-serif;
    font-size: 13px;
}

/* Barra Superior e Entradas */
QLineEdit {
    background-color: #2b2b36;
    border: 1px solid #3d3d4d;
    border-radius: 6px;
    padding: 6px 12px;
    color: #ffffff;
    selection-background-color: #4a5bcf;
}

QLineEdit:focus {
    border: 1px solid #6371de;
}

/* Botões de Navegação e Controlo */
QPushButton {
    background-color: #2b2b36;
    border: 1px solid #3d3d4d;
    border-radius: 6px;
    padding: 6px 12px;
    color: #f0f0f0;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #383847;
    border-color: #525266;
}

QPushButton:pressed {
    background-color: #22222b;
}

/* Seletor de Idiomas */
QComboBox {
    background-color: #2b2b36;
    border: 1px solid #3d3d4d;
    border-radius: 6px;
    padding: 4px 10px;
    color: #f0f0f0;
    min-width: 130px;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #2b2b36;
    border: 1px solid #3d3d4d;
    selection-background-color: #4a5bcf;
    selection-color: #ffffff;
    color: #ffffff;
    outline: none;
}

/* Árvore de Ficheiros e Pastas */
QTreeView {
    background-color: #18181c;
    border: 1px solid #2b2b36;
    border-radius: 8px;
    alternate-background-color: #1f1f26;
    show-decoration-selected: 1;
    outline: none;
}

QTreeView::item {
    height: 28px;
    border-radius: 4px;
    padding-left: 4px;
}

QTreeView::item:hover {
    background-color: #2b2b38;
}

QTreeView::item:selected {
    background-color: #3b4998;
    color: #ffffff;
}

/* Cabeçalho das Colunas */
QHeaderView::section {
    background-color: #22222b;
    color: #a0a0b0;
    padding: 6px 8px;
    border: none;
    border-right: 1px solid #2e2e3a;
    border-bottom: 1px solid #2e2e3a;
    font-weight: 600;
}

/* Menu de Contexto */
QMenu {
    background-color: #262633;
    border: 1px solid #3d3d4d;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px 6px 12px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #4a5bcf;
    color: #ffffff;
}

/* Barra de Scroll */
QScrollBar:vertical {
    border: none;
    background: #18181c;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #383847;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #4e4e63;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("Aetheris", "FileManagerByMiguel")
        
        # Recupera idioma guardado ou assume o padrão
        saved_lang = self.settings.value("language", "pt_PT")
        self.current_lang = saved_lang if saved_lang in TRANSLATIONS else "pt_PT"
        
        self.history = []
        self.history_index = -1
        
        # Forçar independência total de estilo
        self.setStyleSheet(STANDALONE_STYLE)
        
        self.init_ui()
        self.apply_translations()

    def t(self, key):
        return TRANSLATIONS.get(self.current_lang, {}).get(key, key)

    def init_ui(self):
        self.resize(1050, 680)
        self.setMinimumSize(700, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(8)

        # Aviso Root independente (não depende de alertas do sistema)
        is_root = (os.geteuid() == 0)
        show_root_banner = self.settings.value("show_root_banner", "true") == "true"
        
        if is_root and show_root_banner:
            self.root_frame = QFrame()
            self.root_frame.setStyleSheet(
                "background-color: #701a1a; color: #ffdede; border: 1px solid #992626; border-radius: 6px; padding: 6px;"
            )
            root_layout = QHBoxLayout(self.root_frame)
            root_layout.setContentsMargins(10, 4, 10, 4)
            
            self.root_label = QLabel()
            self.root_label.setStyleSheet("font-weight: bold; background: transparent; border: none;")
            
            self.btn_dismiss_root = QPushButton()
            self.btn_dismiss_root.setStyleSheet(
                "background: #4a1212; color: #ffffff; border: 1px solid #701a1a; padding: 4px 10px; border-radius: 4px;"
            )
            self.btn_dismiss_root.clicked.connect(self.dismiss_root_warning)
            
            root_layout.addWidget(self.root_label)
            root_layout.addStretch()
            root_layout.addWidget(self.btn_dismiss_root)
            self.main_layout.addWidget(self.root_frame)
        else:
            self.root_frame = None

        # Barra de Navegação Independente
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(6)
        
        self.btn_back = QPushButton("◀")
        self.btn_back.setFixedWidth(40)
        self.btn_back.clicked.connect(self.nav_back)

        self.btn_forward = QPushButton("▶")
        self.btn_forward.setFixedWidth(40)
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

        # Modelo e Visualizador de Ficheiros
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        self.model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot | QDir.Filter.Hidden)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setAnimated(True)
        self.tree.setSortingEnabled(True)
        self.tree.setAlternatingRowColors(True)
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
            self.open_file_autonomously(path)

    def open_file_autonomously(self, path):
        """Abertura de ficheiro independente de ambiente."""
        try:
            # Tenta xdg-open primeiro se disponível
            if shutil.which("xdg-open"):
                subprocess.Popen(["xdg-open", path], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                return

            # Fallbacks manuais comuns no Linux
            for opener in ["gio", "mimeo", "handlr"]:
                if shutil.which(opener):
                    subprocess.Popen([opener, "open", path], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                    return

            QMessageBox.warning(self, "Aetheris", f"Não foi encontrado um abridor padrão para o ficheiro:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao abrir ficheiro: {e}")

    def open_context_menu(self, position):
        index = self.tree.indexAt(position)
        if not index.isValid():
            return
        path = self.model.filePath(index)
        
        menu = QMenu(self)
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
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self.nav_refresh()
            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))
