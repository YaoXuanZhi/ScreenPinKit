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
        self.settingWindow = None
        self.initUI()
        self.initSystemTrayMenu()
        self.show()

    def initUI(self):
        # self.setWindowIcon(ScreenShotIcon.icon(ScreenShotIcon.LOGO))
        self.setWindowIcon(QIcon(":/qfluentwidgets/images/logo.png"))
        self.setWindowTitle(APP_NAME)

        self.hBoxLayout = QHBoxLayout(self)
        self.button = QPushButton(self.tr("Hello World"))
        self.button.clicked.connect(self.printConfig)
        self.hBoxLayout.addWidget(self.button)        

        self.resize(280, 100)

    def initSystemTrayMenu(self):
        trayMenuActions = [
            Action(ScreenShotIcon.LOGO, self.tr("ScreenShot"), triggered=self.screenShot),
            Action(ScreenShotIcon.SETTING, self.tr("Preferences"), triggered=self.showSettingWindow),
            Action(ScreenShotIcon.QUIT, self.tr("Exit"), triggered=self.exit),
        ]
        self.systemTrayIcon = SystemTrayIcon(self, APP_NAME, self.windowIcon(), trayMenuActions, self.screenShot)
        self.systemTrayIcon.show()

    def printConfig(self):
        print(f"{cfg.get(cfg.dpiScale)}")
        print(f"{cfg.get(cfg.language)}")
        print(f"{cfg.get(cfg.cacheFolder)}")

        print(f"{cfg.get(cfg.screenShotHotKey)}")
        print(f"{cfg.get(cfg.screenPaintHotKey)}")
        print(f"{cfg.get(cfg.mouseThoughHotKey)}")
        print(f"{cfg.get(cfg.showClipboardHotKey)}")

        self.showSettingWindow()

    def screenShot(self):
        print(self.tr("ScreenShot"))

    def screenPaint(self):
        print(self.tr("ScreenPaint"))

    def showSettingWindow(self):
        if self.settingWindow == None:
            self.settingWindow = SettingWindow()
        self.settingWindow.show()

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

    # create application
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # internationalization
    locale = cfg.get(cfg.language).value
    fluentTranslator = FluentTranslator(locale)
    settingTranslator = QTranslator()
    settingTranslator.load(locale, "settings", ".", "resource/i18n")

    app.installTranslator(fluentTranslator)
    app.installTranslator(settingTranslator)

    wnd = MainWindow()

    sys.exit(app.exec_())
