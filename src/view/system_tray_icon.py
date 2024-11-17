# coding=utf-8
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QSystemTrayIcon, QWidget

from qfluentwidgets import SystemTrayMenu


# 托盘菜单
class SystemTrayIcon(QSystemTrayIcon):
    def __init__(
        self,
        parent: QWidget,
        toolTip: str,
        winIcon: QIcon,
        menuActions: list,
        activatedCallback,
    ):
        super().__init__(parent=parent)
        self.setIcon(winIcon)
        self.setToolTip(toolTip)

        self.activatedCallback = activatedCallback
        self.menu = SystemTrayMenu(parent=parent)
        self.menu.addActions(menuActions)
        self.menu.view.setIconSize(QSize(20, 20))
        self.setContextMenu(self.menu)

        self.parent = parent
        self.activated.connect(self.systemTrayIconActivated)

    def systemTrayIconActivated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.activatedCallback:
                self.activatedCallback()
