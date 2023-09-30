import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initUI()


    def initUI(self):
        self.setGeometry(200, 200, 800, 600)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignHCenter)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        label = QLabel("Hello World")
        self.layout.addWidget(label)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    wnd = MainWindow()
    wnd.show()

    sys.exit(app.exec_())
