import sys, os
from common import *
from view import *
from manager import *
from version import *

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settingWindow = None
        self.keyObj = None
        self.screenShotWindow = None
        self.screenPaintWindow = None
        self.initSystemTrayMenu()
        self.initHotKey()
        self.initPinWindowManager()

    def initPinWindowManager(self):
        self.pinWindowMgr = PinWindowManager()

    def initSystemTrayMenu(self):
        trayMenuActions = [
            Action(ScreenShotIcon.SNAP, self.tr("Snap"), triggered=self.screenShot),
            Action(ScreenShotIcon.SETTING, self.tr("Preferences"), triggered=self.showSettingWindow),
            Action(ScreenShotIcon.QUIT, self.tr("Exit"), triggered=self.exit),
        ]
        self.systemTrayIcon = SystemTrayIcon(self, APP_NAME, Icon(ScreenShotIcon.LOGO), trayMenuActions, self.screenShot)
        self.systemTrayIcon.show()

    def initHotKey(self):
        if self.keyObj == None:
            self.keyObj = KeyboardEx()
        self.keyObj.addHotKey(cfg.get(cfg.hotKeyShowClipboard), self.showClipboard)
        self.keyObj.addHotKey(cfg.get(cfg.hotKeyScreenPaint), self.screenPaint)
        self.keyObj.addHotKey(cfg.get(cfg.hotKeyScreenShot), self.screenShot)
        self.keyObj.addHotKey(cfg.get(cfg.hotKeyToggleMouseClickThrough), self.switchMouseThroughState)
        self.keyObj.addHotKey(cfg.get(cfg.hotKeySwitchScreenPaintMode), self.switchScreenPaintMode)

    def screenShot(self):
        if self.screenShotWindow == None:
            self.screenShotWindow = ScreenShotWindow()
            self.screenShotWindow.snipedSignal.connect(self.pinWindowMgr.snip)
            self.screenShotWindow.closedSignal.connect(self.onScreenShotWindowClosed)
        self.screenShotWindow.reShow()

    def screenPaint(self):
        if self.screenPaintWindow == None:
            self.screenPaintWindow = ScreenPaintWindow()
            self.screenPaintWindow.show()
        else:
            self.screenPaintWindow.startDraw()

    def showClipboard(self):
        self.pinWindowMgr.showClipboard()

    def showSettingWindow(self):
        if self.settingWindow == None:
            self.settingWindow = SettingWindow()
        self.settingWindow.show()

    def switchScreenPaintMode(self):
        if self.screenPaintWindow == None:
            return

        if self.screenPaintWindow.isVisible():
            self.screenPaintWindow.canvasEditor.completeDraw()
            self.screenPaintWindow.hide()
        else:
            self.screenPaintWindow.show()

    def switchMouseThroughState(self):
        self.pinWindowMgr.switchMouseThroughState()

    def onScreenShotWindowClosed(self):
        self.screenShotWindow.destroy()
        self.screenShotWindow = None

    def exit(self):
        sys.exit(0)

def main():
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
    settingTranslator.load(locale, "settings", ".", ":/ScreenPinKit/resource/i18n")

    app.installTranslator(fluentTranslator)
    app.installTranslator(settingTranslator)

    MainWindow()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()