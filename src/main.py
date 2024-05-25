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
        self.keyObj = None
        self.initSystemTrayMenu()
        self.initHotKey()

    def initSystemTrayMenu(self):
        trayMenuActions = [
            Action(ScreenShotIcon.LOGO, self.tr("ScreenShot"), triggered=self.screenShot),
            Action(ScreenShotIcon.SETTING, self.tr("Preferences"), triggered=self.showSettingWindow),
            Action(ScreenShotIcon.QUIT, self.tr("Exit"), triggered=self.exit),
        ]
        self.systemTrayIcon = SystemTrayIcon(self, APP_NAME, QIcon(":/qfluentwidgets/images/logo.png"), trayMenuActions, self.screenShot)
        self.systemTrayIcon.show()

    def initHotKey(self):
        if self.keyObj == None:
            self.keyObj = KeyboardEx()
        self.keyObj.addHotKey(cfg.get(cfg.showClipboardHotKey), self.showClipboard)
        self.keyObj.addHotKey(cfg.get(cfg.screenPaintHotKey), self.screenPaint)
        self.keyObj.addHotKey(cfg.get(cfg.screenShotHotKey), self.screenShot)
        self.keyObj.addHotKey(cfg.get(cfg.mouseThoughHotKey), self.switchMouseThroughState)
        self.keyObj.addHotKey(cfg.get(cfg.switchScreenPaintModeHotKey), self.switchScreenPaintMode)

    def screenShot(self):
        print(self.tr("ScreenShot"))

    def screenPaint(self):
        print(self.tr("ScreenPaint"))

    def showClipboard(self):
        print(self.tr("ShowClipboard"))

    def showSettingWindow(self):
        if self.settingWindow == None:
            self.settingWindow = SettingWindow()
        self.settingWindow.show()

    def switchScreenPaintMode(self):
        print(self.tr("SwitchScreenPaintMode"))

    def switchMouseThroughState(self):
        print(self.tr("SwitchMouseThroughState"))

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
