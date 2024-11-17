# coding=utf-8
import sys, os, random
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from canvas_item import *


class MainWindow(QLabel):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Full Screen Example")
        self.showFullScreen()  # 进入全屏模式
        self.defaultFlag()

    def defaultFlag(self):
        self.setMouseTracking(True)
        # self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:  # 按下 Esc 键退出全屏模式
            self.showNormal()

    def showFullScreen(self):
        # 获取屏幕几何信息
        finalPixmap, finalGeometry = CanvasUtil.grabScreens()

        # 设置窗口大小为屏幕大小
        self.setPixmap(finalPixmap)
        self.setGeometry(finalGeometry)
        super().showFullScreen()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
