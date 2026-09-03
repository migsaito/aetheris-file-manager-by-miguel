import sys
import os

# 1. FORÇAR INDEPENDÊNCIA GRÁFICA TOTAL:
# Desativa temas externos do sistema (Kvantum, qt5ct, qt6ct, gtk2/3 engines)
os.environ["QT_QPA_PLATFORMTHEME"] = ""
os.environ["QT_STYLE_OVERRIDE"] = ""
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt
from aetheris_fm.ui import MainWindow

def create_standalone_palette():
    """Garante cores idênticas em qualquer distro e ambiente gráfico."""
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#1e1e24"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#e0e0e0"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#18181c"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#1f1f26"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#2b2b36"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#2b2b36"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#f0f0f0"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#ff5555"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#4a5bcf"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    return palette

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Aetheris File Manager by Miguel")
    
    # Força renderizador neutro embutido Fusion e a paleta própria
    app.setStyle("Fusion")
    app.setPalette(create_standalone_palette())
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
