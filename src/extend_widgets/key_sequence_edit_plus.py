# coding=utf-8
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import *
from common import ScreenShotIcon


class KeySequenceEditPlus(QFrame):
    def __init__(self, hotkey: str, parent=None):
        super().__init__(parent=parent)
        self.setStyleSheet("""
            QKeySequenceEdit{
                font: 13px 'Microsoft YaHei Light';
                background: rgb(242,242,242);
                text-align: center;
            }
        """)
        self.resize(250, 20)
        self.keySequenceEdit = QKeySequenceEdit(self)
        self.cancelButton = CommandButton(
            FluentIcon.icon(ScreenShotIcon.ERROR_LIGHT), self
        )
        self.cancelButton.clicked.connect(self.onClearKeySequence)
        self.stateIconWidget = IconWidget(ScreenShotIcon.SUCCESS_LIGHT, self)
        self.keySequenceEdit.keySequenceChanged.connect(self.__onKeySequenceChanged)
        defaultKeySequence = QKeySequence(hotkey)
        self.keySequenceEdit.setKeySequence(defaultKeySequence)
        self.updateState(QKeySequence(hotkey))
        self.__initWidget()

    def onClearKeySequence(self):
        self.keySequenceEdit.setKeySequence(QKeySequence())
        self.cancelButton.setEnabled(False)
        self.cancelButton.setIcon(QIcon())
        self.stateIconWidget.setIcon(QIcon())

    def __onKeySequenceChanged(self, keySequence: QKeySequence):
        self.updateState(keySequence)

    def updateState(self, keySequence: QKeySequence):
        if keySequence.isEmpty():
            self.cancelButton.setEnabled(False)
            self.cancelButton.setIcon(QIcon())
            self.stateIconWidget.setIcon(QIcon())
        else:
            self.cancelButton.setEnabled(True)
            self.cancelButton.setIcon(FluentIcon.icon(ScreenShotIcon.ERROR_LIGHT))
            self.stateIconWidget.setIcon(FluentIcon.icon(ScreenShotIcon.SUCCESS_LIGHT))

    def __initWidget(self):
        self.keySequenceEdit.setFixedSize(200, 20)
        self.stateIconWidget.setFixedSize(18, 18)
        self.cancelButton.setFixedSize(18, 18)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.keySequenceEdit, 0, Qt.AlignmentFlag.AlignLeft)
        self.hBoxLayout.addSpacing(-28)
        self.hBoxLayout.addWidget(self.cancelButton)
        self.hBoxLayout.addSpacing(6)
        self.hBoxLayout.addWidget(self.stateIconWidget)
