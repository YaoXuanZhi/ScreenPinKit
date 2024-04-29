import sys, math
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from hotkey import KeyboardEx
from icon import ScreenShotIcon
from qfluentwidgets import Action
from system_tray_icon import SystemTrayIcon
from screen_shot_window import ScreenShotWindow
from screen_paint_window import ScreenPaintWindow

class SettingWindow(QWidget):
    def __init__(self):
        super().__init__()

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initSystemTrayMenu()
        self.screenShotWindow = ScreenShotWindow()

        keyObj = KeyboardEx()
        keyObj.addHotKey("f10", self.pasteScreen)
        keyObj.addHotKey("f4", lambda: self.screenPaint())
        keyObj.addHotKey("f7", self.screenShot)
        keyObj.addHotKey("alt+f", lambda: self.screenShotWindow.switchMouseThroughState())

    def initSystemTrayMenu(self):
        self.setWindowIcon(ScreenShotIcon.icon(ScreenShotIcon.LOGO))
        trayMenuActions = [
            Action(ScreenShotIcon.LOGO, '截图', triggered=self.screenShot),
            Action(ScreenShotIcon.SETTING, '首选项', triggered=self.showSettingWindow),
            Action(ScreenShotIcon.QUIT, '退出', triggered=self.exit),
            Action(ScreenShotIcon.FINISHED, '关闭鼠标穿透', triggered=self.removeMouseThougth),
            Action(ScreenShotIcon.WHITE_BOARD, '桌面标注', triggered=self.screenPaint),
        ]
        self.systemTrayIcon = SystemTrayIcon(self, "截图工具", self.windowIcon(), trayMenuActions, self.screenShot)
        self.systemTrayIcon.show()

    def pasteScreen(self):
        '''贴图'''

    def screenShot(self):
        '''屏幕截图'''
        self.screenShotWindow.reShow()

    def screenPaint(self):
        '''屏幕绘图'''
        if not hasattr(self, "screenPaintWindow"):
            self.screenPaintWindow = ScreenPaintWindow()
            self.screenPaintWindow.show()
        else:
            self.screenPaintWindow.startDraw()

    def exit(self):
        sys.exit(0)

    def removeMouseThougth(self):
        for wnd in self.screenShotWindow.freeze_imgs:
            if wnd != None:
                wnd.setMouseThroughState(False)

    def showSettingWindow(self):
        self.settingWindow = SettingWindow()
        self.settingWindow.show()


if __name__ == '__main__':
    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    wnd = MainWindow()

    sys.exit(app.exec_())
