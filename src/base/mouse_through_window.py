from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class MouseThroughWindow(QWidget):
    '''支持鼠标穿透窗口类'''
    def __init__(self, parent:QWidget = None):
        super().__init__(parent)

    def setVisible(self, visible: bool) -> None:
        # [Qt之使用setWindowFlags方法遇到的问题](https://blog.csdn.net/goforwardtostep/article/details/68938965/)
        setMouseThroughing = False
        if hasattr(self, "setMouseThroughing"):
            setMouseThroughing = self.setMouseThroughing

        if setMouseThroughing:
            return
        return super().setVisible(visible)

    def setMouseThroughState(self, isThrough:bool):
        self.setMouseThroughing = True
        self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, isThrough)
        self.setMouseThroughing = False
        self.show()

    def isMouseThrough(self):
        return (self.windowFlags() | Qt.WindowType.WindowTransparentForInput) == self.windowFlags()

    # 切换鼠标穿透状态
    def switchMouseThroughState(self):
        if self.isMouseThrough():
            self.setMouseThroughState(False)
        else:
            self.setMouseThroughState(True)