import sys
from PyQt6.QtWidgets import QApplication
from aetheris_fm.ui import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Aetheris File Manager by Miguel")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
