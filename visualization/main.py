import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import BrainNetworkAnalysisGUI

def load_stylesheet(path):
    """Load and return the content of the QSS file."""
    with open(path, "r") as file:
        return file.read()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Apply the style sheet
    stylesheet_path = "gui/styles.qss"
    app.setStyleSheet(load_stylesheet(stylesheet_path))

    # Start the application
    window = BrainNetworkAnalysisGUI()
    window.show()
    sys.exit(app.exec())
