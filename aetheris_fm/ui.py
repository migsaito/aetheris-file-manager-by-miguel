import os
import sys
import shutil
import subprocess
import stat
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                             QHeaderView, QComboBox, QSplitter, QListWidget, QListWidgetItem,
                             QStatusBar, QMenu, QMessageBox, QInputDialog, QStyle)
from PyQt6.QtGui import QIcon, QColor, QAction, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, QSize
from aetheris_fm.locales import TRANSLATIONS

class NumericTableWidgetItem(QTableWidgetItem):
    def __init__(self, text, sort_value):
        super().__init__(text)
        self.sort_value = sort_value

    def __lt__(self, other):
        if isinstance(other, NumericTableWidgetItem):
            return self.sort_value < other.sort_value
        return super().__lt__(other)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_path = os.path.expanduser("~")
        self.current_language = "English (US)"
        self.show_hidden = False
        self.clipboard_paths = []
        self.clipboard_action = None
        self.init_ui()

    def get_theme_icon(self, icon_name, fallback_standard):
        icon = QIcon.fromTheme(icon_name)
        if icon.isNull():
            return self.style().standardIcon(fallback_standard)
        return icon

    def init_ui(self):
        self.setWindowTitle("Aetheris File Manager by Miguel")
        self.resize(1150, 750)

        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logo.png")
        if not os.path.exists(icon_path):
            icon_path = "/usr/share/pixmaps/aetheris-file-manager-by-miguel.png"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            self.setWindowIcon(self.get_theme_icon("system-file-manager", QStyle.StandardPixmap.SP_DirIcon))

        self.setup_menu_bar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        self.btn_back = QPushButton()
        self.btn_back.setIcon(self.get_theme_icon("go-previous", QStyle.StandardPixmap.SP_ArrowLeft))
        self.btn_back.setFixedSize(40, 35)
        self.btn_back.clicked.connect(self.go_back)

        self.btn_forward = QPushButton()
        self.btn_forward.setIcon(self.get_theme_icon("go-next", QStyle.StandardPixmap.SP_ArrowRight))
        self.btn_forward.setFixedSize(40, 35)
        self.btn_forward.clicked.connect(self.go_forward)
        self.btn_forward.setEnabled(False)

        self.btn_home = QPushButton()
        self.btn_home.setFixedHeight(35)
        self.btn_home.setIcon(self.get_theme_icon("go-home", QStyle.StandardPixmap.SP_DirHomeIcon))
        self.btn_home.clicked.connect(self.go_home)

        self.btn_refresh = QPushButton()
        self.btn_refresh.setFixedHeight(35)
        self.btn_refresh.setIcon(self.get_theme_icon("view-refresh", QStyle.StandardPixmap.SP_BrowserReload))
        self.btn_refresh.clicked.connect(self.populate_list)

        self.path_input = QLineEdit()
        self.path_input.setFixedHeight(35)
        self.path_input.setStyleSheet("padding: 0 10px; font-size: 14px;")
        self.path_input.returnPressed.connect(self.navigate_from_input)

        self.search_input = QLineEdit()
        self.search_input.setFixedHeight(35)
        self.search_input.setFixedWidth(250)
        self.search_input.setStyleSheet("padding: 0 10px; font-size: 14px;")
        self.search_input.textChanged.connect(self.filter_items)

        self.combo_lang = QComboBox()
        self.combo_lang.setFixedHeight(35)
        self.combo_lang.setStyleSheet("padding: 0 10px; font-size: 14px;")
        self.combo_lang.addItems(TRANSLATIONS.keys())
        self.combo_lang.currentTextChanged.connect(self.change_language)

        top_bar.addWidget(self.btn_back)
        top_bar.addWidget(self.btn_forward)
        top_bar.addWidget(self.btn_home)
        top_bar.addWidget(self.btn_refresh)
        top_bar.addWidget(self.path_input)
        top_bar.addWidget(self.search_input)
        top_bar.addWidget(self.combo_lang)

        main_layout.addLayout(top_bar)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setIconSize(QSize(20, 20))
        self.sidebar.setStyleSheet("""
            QListWidget { font-size: 14px; padding: 5px; outline: 0; }
            QListWidget::item { padding: 8px; margin-bottom: 2px; border-radius: 4px; }
            QListWidget::item:selected { background-color: #313244; }
        """)
        self.sidebar.itemClicked.connect(self.sidebar_nav)
        self.splitter.addWidget(self.sidebar)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setIconSize(QSize(24, 24))
        self.table.setStyleSheet("""
            QTableWidget { font-size: 14px; outline: 0; }
            QTableWidget::item { padding: 4px; }
        """)
        
        self.table.cellDoubleClicked.connect(self.on_item_double_clicked)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.open_context_menu)
        self.table.itemSelectionChanged.connect(self.update_status_bar)

        self.splitter.addWidget(self.table)
        self.splitter.setSizes([220, 930])
        main_layout.addWidget(self.splitter)

        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("font-size: 13px;")
        self.setStatusBar(self.status_bar)

        self.history_back = []
        self.history_forward = []

        self.setup_shortcuts()
        self.update_sidebar()
        
        saved_lang_index = self.combo_lang.findText("Português (Brasil)")
        if saved_lang_index >= 0:
            self.combo_lang.setCurrentIndex(saved_lang_index)
        else:
            self.change_language("English (US)")

    def setup_menu_bar(self):
        menubar = self.menuBar()
        self.menu_file = menubar.addMenu("File")
        self.menu_view = menubar.addMenu("View")
        self.menu_help = menubar.addMenu("Help")

        self.action_new_folder = QAction("New Folder", self)
        self.action_new_folder.triggered.connect(self.create_folder)
        self.action_new_file = QAction("New File", self)
        self.action_new_file.triggered.connect(self.create_file)
        self.action_exit = QAction("Exit", self)
        self.action_exit.triggered.connect(self.close)

        self.menu_file.addAction(self.action_new_folder)
        self.menu_file.addAction(self.action_new_file)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_exit)

        self.action_toggle_hidden = QAction("Show Hidden Files", self, checkable=True)
        self.action_toggle_hidden.setChecked(self.show_hidden)
        self.action_toggle_hidden.triggered.connect(self.toggle_hidden_menu)
        self.action_refresh = QAction("Refresh", self)
        self.action_refresh.triggered.connect(self.populate_list)

        self.menu_view.addAction(self.action_toggle_hidden)
        self.menu_view.addAction(self.action_refresh)

        self.action_about = QAction("About Aetheris", self)
        self.action_about.triggered.connect(self.show_about)
        self.menu_help.addAction(self.action_about)

    def show_about(self):
        t = TRANSLATIONS[self.current_language]
        QMessageBox.about(self, t["menu_about"], "Aetheris File Manager\nCreated by Miguel Saito Garcia.\nBuilt with PyQt6 on Arch Linux.")

    def toggle_hidden_menu(self, state):
        self.show_hidden = state
        self.populate_list()

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+H"), self).activated.connect(self.toggle_hidden_shortcut)
        QShortcut(QKeySequence("F5"), self).activated.connect(self.populate_list)
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self.populate_list)
        QShortcut(QKeySequence("Alt+Up"), self).activated.connect(self.go_up)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self.delete_selected)
        QShortcut(QKeySequence("F2"), self).activated.connect(self.rename_selected)
        QShortcut(QKeySequence("Ctrl+C"), self).activated.connect(self.copy_selected)
        QShortcut(QKeySequence("Ctrl+X"), self).activated.connect(self.cut_selected)
        QShortcut(QKeySequence("Ctrl+V"), self).activated.connect(self.paste_items)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.search_input.setFocus)

    def toggle_hidden_shortcut(self):
        self.show_hidden = not self.show_hidden
        self.action_toggle_hidden.setChecked(self.show_hidden)
        self.populate_list()

    def go_up(self):
        parent_dir = os.path.dirname(self.current_path)
        if parent_dir != self.current_path:
            self.navigate(parent_dir)

    def change_language(self, lang):
        self.current_language = lang
        t = TRANSLATIONS[lang]
        self.btn_home.setText(t["home"])
        self.btn_refresh.setText(t["refresh"])
        self.search_input.setPlaceholderText(t["search_placeholder"])
        
        self.menu_file.setTitle(t["menu_file"])
        self.menu_view.setTitle(t["menu_view"])
        self.menu_help.setTitle(t["menu_help"])
        
        self.action_new_folder.setText(t["new_folder"])
        self.action_new_file.setText(t["new_file"])
        self.action_exit.setText(t["menu_exit"])
        self.action_toggle_hidden.setText(t["menu_hidden"])
        self.action_refresh.setText(t["refresh"])
        self.action_about.setText(t["menu_about"])

        self.table.setHorizontalHeaderLabels([t["name"], t["size"], t["type"], t["date_modified"]])
        self.update_sidebar()
        self.populate_list()

    def update_sidebar(self):
        self.sidebar.clear()
        t = TRANSLATIONS[self.current_language]
        
        places = [
            (t["home"], os.path.expanduser("~"), "user-home"),
            (t["documents"], os.path.expanduser("~/Documents"), "folder-documents"),
            (t["downloads"], os.path.expanduser("~/Downloads"), "folder-download"),
            (t["pictures"], os.path.expanduser("~/Pictures"), "folder-pictures"),
            (t["music"], os.path.expanduser("~/Music"), "folder-music"),
            (t["videos"], os.path.expanduser("~/Videos"), "folder-videos"),
            (t["root"], "/", "drive-harddisk"),
        ]
        
        for name, path, icon_name in places:
            if os.path.exists(path) or path == "/":
                icon = self.get_theme_icon(icon_name, QStyle.StandardPixmap.SP_DirIcon)
                item = QListWidgetItem(icon, name)
                item.setData(Qt.ItemDataRole.UserRole, path)
                self.sidebar.addItem(item)

    def sidebar_nav(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        self.navigate(path)

    def navigate(self, path):
        if os.path.isdir(path):
            if self.current_path:
                self.history_back.append(self.current_path)
                self.btn_back.setEnabled(True)
            self.history_forward.clear()
            self.btn_forward.setEnabled(False)
            self.current_path = path
            self.path_input.setText(path)
            self.search_input.clear()
            self.populate_list()

    def navigate_from_input(self):
        path = self.path_input.text()
        if os.path.exists(path) and os.path.isdir(path):
            self.navigate(path)
        else:
            self.path_input.setText(self.current_path)

    def go_back(self):
        if self.history_back:
            self.history_forward.append(self.current_path)
            self.btn_forward.setEnabled(True)
            self.current_path = self.history_back.pop()
            if not self.history_back:
                self.btn_back.setEnabled(False)
            self.path_input.setText(self.current_path)
            self.search_input.clear()
            self.populate_list()

    def go_forward(self):
        if self.history_forward:
            self.history_back.append(self.current_path)
            self.btn_back.setEnabled(True)
            self.current_path = self.history_forward.pop()
            if not self.history_forward:
                self.btn_forward.setEnabled(False)
            self.path_input.setText(self.current_path)
            self.search_input.clear()
            self.populate_list()

    def go_home(self):
        self.navigate(os.path.expanduser("~"))

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    def get_icon_for_file(self, filename):
        ext = filename.lower().split('.')[-1] if '.' in filename else ""
        if ext in ['png', 'jpg', 'jpeg', 'svg', 'gif', 'bmp']:
            return self.get_theme_icon("image-x-generic", QStyle.StandardPixmap.SP_FileIcon)
        elif ext in ['mp4', 'mkv', 'avi', 'webm', 'mov']:
            return self.get_theme_icon("video-x-generic", QStyle.StandardPixmap.SP_FileIcon)
        elif ext in ['mp3', 'wav', 'flac', 'ogg']:
            return self.get_theme_icon("audio-x-generic", QStyle.StandardPixmap.SP_FileIcon)
        elif ext in ['zip', 'tar', 'gz', 'rar', '7z', 'xz']:
            return self.get_theme_icon("package-x-generic", QStyle.StandardPixmap.SP_FileIcon)
        elif ext in ['txt', 'md', 'csv', 'json']:
            return self.get_theme_icon("text-x-generic", QStyle.StandardPixmap.SP_FileIcon)
        elif ext in ['py', 'sh', 'cpp', 'c', 'js', 'html', 'css']:
            return self.get_theme_icon("text-x-script", QStyle.StandardPixmap.SP_FileIcon)
        elif ext in ['pdf']:
            return self.get_theme_icon("application-pdf", QStyle.StandardPixmap.SP_FileIcon)
        else:
            return self.get_theme_icon("application-x-generic", QStyle.StandardPixmap.SP_FileIcon)

    def get_icon_for_directory(self, dirname):
        name = dirname.lower()
        if name in ['downloads', 'transferências', 'descargas']:
            return self.get_theme_icon("folder-download", QStyle.StandardPixmap.SP_DirIcon)
        elif name in ['documents', 'documentos', 'dokumente']:
            return self.get_theme_icon("folder-documents", QStyle.StandardPixmap.SP_DirIcon)
        elif name in ['pictures', 'imagens', 'imágenes', 'bilder']:
            return self.get_theme_icon("folder-pictures", QStyle.StandardPixmap.SP_DirIcon)
        elif name in ['music', 'músicas', 'música', 'musik']:
            return self.get_theme_icon("folder-music", QStyle.StandardPixmap.SP_DirIcon)
        elif name in ['videos', 'vídeos']:
            return self.get_theme_icon("folder-videos", QStyle.StandardPixmap.SP_DirIcon)
        elif name in ['desktop', 'área de trabalho', 'escritorio']:
            return self.get_theme_icon("user-desktop", QStyle.StandardPixmap.SP_DirIcon)
        elif name in ['public', 'público']:
            return self.get_theme_icon("folder-public", QStyle.StandardPixmap.SP_DirIcon)
        elif name in ['templates', 'modelos']:
            return self.get_theme_icon("folder-templates", QStyle.StandardPixmap.SP_DirIcon)
        else:
            return self.get_theme_icon("folder", QStyle.StandardPixmap.SP_DirIcon)

    def populate_list(self):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        try:
            items = os.listdir(self.current_path)
        except PermissionError:
            self.table.setSortingEnabled(True)
            return

        directories = []
        files = []
        t = TRANSLATIONS[self.current_language]

        for item in items:
            if not self.show_hidden and item.startswith('.'):
                continue
            full_path = os.path.join(self.current_path, item)
            try:
                stat_info = os.stat(full_path)
                mtime = datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M')
                
                if stat.S_ISDIR(stat_info.st_mode):
                    icon = self.get_icon_for_directory(item)
                    directories.append((item, 0, "", t["folder"], mtime, full_path, icon))
                else:
                    raw_size = stat_info.st_size
                    fmt_size = self.format_size(raw_size)
                    icon = self.get_icon_for_file(item)
                    files.append((item, raw_size, fmt_size, t["file"], mtime, full_path, icon))
            except Exception:
                continue

        directories.sort(key=lambda x: x[0].lower())
        files.sort(key=lambda x: x[0].lower())
        all_items = directories + files

        self.table.setRowCount(len(all_items))
        for row, data in enumerate(all_items):
            item_name = QTableWidgetItem(data[6], data[0])
            item_name.setData(Qt.ItemDataRole.UserRole, data[5])
            if data[3] == t["folder"]:
                item_name.setForeground(QColor("#89b4fa"))
            
            item_size = NumericTableWidgetItem(data[2], data[1])
            item_type = QTableWidgetItem(data[3])
            item_date = QTableWidgetItem(data[4])

            self.table.setItem(row, 0, item_name)
            self.table.setItem(row, 1, item_size)
            self.table.setItem(row, 2, item_type)
            self.table.setItem(row, 3, item_date)

        self.table.setSortingEnabled(True)
        self.update_status_bar()

    def filter_items(self, query):
        query = query.lower()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if query in item.text().lower():
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def on_item_double_clicked(self, row, column):
        item = self.table.item(row, 0)
        full_path = item.data(Qt.ItemDataRole.UserRole)
        if os.path.isdir(full_path):
            self.navigate(full_path)
        else:
            if sys.platform.startswith('linux'):
                subprocess.Popen(['xdg-open', full_path])

    def open_context_menu(self, position):
        menu = QMenu()
        t = TRANSLATIONS[self.current_language]

        action_terminal = QAction(self.get_theme_icon("utilities-terminal", QStyle.StandardPixmap.SP_ComputerIcon), t["open_terminal"], self)
        action_terminal.triggered.connect(self.open_terminal)
        menu.addAction(action_terminal)
        menu.addSeparator()

        selected_items = self.table.selectedItems()
        if not selected_items:
            action_new_folder = QAction(self.get_theme_icon("folder-new", QStyle.StandardPixmap.SP_DirIcon), t["new_folder"], self)
            action_new_folder.triggered.connect(self.create_folder)
            action_new_file = QAction(self.get_theme_icon("document-new", QStyle.StandardPixmap.SP_FileIcon), t["new_file"], self)
            action_new_file.triggered.connect(self.create_file)
            
            menu.addAction(action_new_folder)
            menu.addAction(action_new_file)
            
            if self.clipboard_paths:
                menu.addSeparator()
                action_paste = QAction(self.get_theme_icon("edit-paste", QStyle.StandardPixmap.SP_FileIcon), t["paste"], self)
                action_paste.triggered.connect(self.paste_items)
                menu.addAction(action_paste)
        else:
            action_copy = QAction(self.get_theme_icon("edit-copy", QStyle.StandardPixmap.SP_FileIcon), t["copy"], self)
            action_copy.triggered.connect(self.copy_selected)
            action_cut = QAction(self.get_theme_icon("edit-cut", QStyle.StandardPixmap.SP_FileIcon), t["cut"], self)
            action_cut.triggered.connect(self.cut_selected)
            action_rename = QAction(t["rename"], self)
            action_rename.triggered.connect(self.rename_selected)
            action_delete = QAction(self.get_theme_icon("edit-delete", QStyle.StandardPixmap.SP_TrashIcon), t["delete"], self)
            action_delete.triggered.connect(self.delete_selected)
            
            menu.addAction(action_copy)
            menu.addAction(action_cut)
            menu.addAction(action_rename)
            menu.addAction(action_delete)

        menu.exec(self.table.viewport().mapToGlobal(position))

    def get_selected_paths(self):
        paths = []
        for item in self.table.selectedItems():
            if item.column() == 0:
                paths.append(item.data(Qt.ItemDataRole.UserRole))
        return paths

    def open_terminal(self):
        try:
            subprocess.Popen(['konsole', '--workdir', self.current_path])
        except Exception:
            try:
                subprocess.Popen(['xterm', '-e', f'cd {self.current_path} && bash'])
            except Exception:
                pass

    def create_folder(self):
        t = TRANSLATIONS[self.current_language]
        text, ok = QInputDialog.getText(self, t["new_folder"], t["enter_name"])
        if ok and text:
            try:
                os.makedirs(os.path.join(self.current_path, text), exist_ok=True)
                self.populate_list()
            except Exception as e:
                QMessageBox.critical(self, t["error"], str(e))

    def create_file(self):
        t = TRANSLATIONS[self.current_language]
        text, ok = QInputDialog.getText(self, t["new_file"], t["enter_name"])
        if ok and text:
            try:
                open(os.path.join(self.current_path, text), 'a').close()
                self.populate_list()
            except Exception as e:
                QMessageBox.critical(self, t["error"], str(e))

    def copy_selected(self):
        self.clipboard_paths = self.get_selected_paths()
        self.clipboard_action = "copy"

    def cut_selected(self):
        self.clipboard_paths = self.get_selected_paths()
        self.clipboard_action = "cut"

    def paste_items(self):
        if not self.clipboard_paths: return
        t = TRANSLATIONS[self.current_language]
        for path in self.clipboard_paths:
            target = os.path.join(self.current_path, os.path.basename(path))
            try:
                if self.clipboard_action == "copy":
                    if os.path.isdir(path):
                        shutil.copytree(path, target)
                    else:
                        shutil.copy2(path, target)
                elif self.clipboard_action == "cut":
                    shutil.move(path, target)
            except Exception as e:
                QMessageBox.critical(self, t["error"], str(e))
                
        if self.clipboard_action == "cut":
            self.clipboard_paths = []
            self.clipboard_action = None
        self.populate_list()

    def rename_selected(self):
        paths = self.get_selected_paths()
        if not paths: return
        target = paths[0]
        t = TRANSLATIONS[self.current_language]
        text, ok = QInputDialog.getText(self, t["rename"], t["enter_name"], text=os.path.basename(target))
        if ok and text:
            try:
                os.rename(target, os.path.join(self.current_path, text))
                self.populate_list()
            except Exception as e:
                QMessageBox.critical(self, t["error"], str(e))

    def delete_selected(self):
        paths = self.get_selected_paths()
        t = TRANSLATIONS[self.current_language]
        for path in paths:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except Exception as e:
                QMessageBox.critical(self, t["error"], str(e))
        self.populate_list()

    def update_status_bar(self):
        t = TRANSLATIONS[self.current_language]
        total = self.table.rowCount()
        selected = len(self.get_selected_paths())
        try:
            usage = shutil.disk_usage(self.current_path)
            free = self.format_size(usage.free)
        except Exception:
            free = "N/A"
        msg = f"{total} {t['items']} | {selected} {t['selected']} | {t['free_space']}: {free}"
        self.status_bar.showMessage(msg)
