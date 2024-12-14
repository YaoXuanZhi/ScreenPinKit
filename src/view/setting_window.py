# coding=utf-8
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from version import *
from qframelesswindow import FramelessWindow, StandardTitleBar
from qfluentwidgets import *
from .setting_interface import *


class SettingWindow(FramelessWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.defaultFlag()
        self.initUI()

    def defaultFlag(self) -> None:
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

    def initUI(self):
        self.setTitleBar(StandardTitleBar(self))
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.settingInterface = SettingInterface(self)
        self.hBoxLayout.addWidget(self.settingInterface)

        self.resize(1080, 784)
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        self.setWindowIcon(Icon(ScreenShotIcon.LOGO))
        self.setWindowTitle(APP_NAME + " " + self.tr("Preferences"))
        self.titleBar.raise_()

    def keyPressEvent(self, a0):
        if a0.key() == Qt.Key_Escape:
            self.close()
        return super().keyPressEvent(a0)