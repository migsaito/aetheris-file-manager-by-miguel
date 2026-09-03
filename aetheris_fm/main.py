import sys
import os
os.environ["QT_QPA_PLATFORMTHEME"] = ""
os.environ["QT_STYLE_OVERRIDE"] = ""
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor, QIcon
from PyQt6.QtCore import Qt
from aetheris_fm.ui import MainWindow

def create_standalone_palette():
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#1e1e2e"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#cdd6f4"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#181825"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#1e1e2e"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#313244"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#cdd6f4"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#cdd6f4"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#313244"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#cdd6f4"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#f38ba8"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#89b4fa"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#1e1e2e"))
    return palette

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Aetheris File Manager by Miguel")
    app.setDesktopFileName("aetheris-file-manager-by-miguel")
    app.setStyle("Fusion")
    app.setPalette(create_standalone_palette())
    
    icon_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "logo.png"),
        "/usr/share/pixmaps/aetheris-file-manager-by-miguel.png",
        os.path.expanduser("~/aetheris-file-manager-by-miguel/logo.png")
    ]
    for p in icon_paths:
        if os.path.exists(p):
            app.setWindowIcon(QIcon(p))
            break

    window = MainWindow()
    for p in icon_paths:
        if os.path.exists(p):
            window.setWindowIcon(QIcon(p))
            break
            
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
