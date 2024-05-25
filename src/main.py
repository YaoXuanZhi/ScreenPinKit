import sys, math, os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from qfluentwidgets import *
from common import *
from view import *

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.initSystemTrayMenu()

        self.hBoxLayout = QHBoxLayout(self)
        self.button = QPushButton("Hello World")
        self.button.clicked.connect(self.printConfig)
        self.hBoxLayout.addWidget(self.button)
        
        self.show()

    def initSystemTrayMenu(self):
        self.setWindowIcon(ScreenShotIcon.icon(ScreenShotIcon.LOGO))
        trayMenuActions = [
            Action(ScreenShotIcon.LOGO, '截图', triggered=self.screenShot),
            Action(ScreenShotIcon.SETTING, '首选项', triggered=self.showSettingWindow),
            Action(ScreenShotIcon.QUIT, '退出', triggered=self.exit),
        ]
        self.systemTrayIcon = SystemTrayIcon(self, "ScreenPinKit", self.windowIcon(), trayMenuActions, self.screenShot)
        self.systemTrayIcon.show()

    def printConfig(self):
        print(f"{cfg.get(cfg.dpiScale)}")
        print(f"{cfg.get(cfg.language)}")
        print(f"{cfg.get(cfg.cacheFolder)}")

        print(f"{cfg.get(cfg.screenShotHotKey)}")
        print(f"{cfg.get(cfg.screenPaintHotKey)}")
        print(f"{cfg.get(cfg.mouseThoughHotKey)}")
        print(f"{cfg.get(cfg.showClipboardHotKey)}")

    def screenShot(self):
        print("屏幕截图")

    def screenPaint(self):
        print("屏幕绘图")

    def showSettingWindow(self):
        print("打开设置界面")

    def exit(self):
        sys.exit(0)

if __name__ == '__main__':
    # enable dpi scale
    if cfg.get(cfg.dpiScale) == "Auto":
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    else:
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    wnd = MainWindow()

    sys.exit(app.exec_())
