import typing
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .mouse_through_window import MouseThroughWindow


class DragWindow(MouseThroughWindow):
    """拖曳移动窗口类"""

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.drag = False

    @typing.overload
    def isAllowDrag(self):
        return False

    def startDrag(self):
        pass

    def endDrag(self):
        pass

    def mousePressEvent(self, event):
        if not self.isAllowDrag():
            return super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag = True
            self.posX, self.posY = event.x(), event.y()
            self.startDrag()

    def mouseReleaseEvent(self, event):
        if not self.isAllowDrag():
            return super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag = False
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            self.endDrag()

    def mouseMoveEvent(self, event):
        if not self.isAllowDrag():
            return super().mouseMoveEvent(event)
        if self.isVisible():
            if self.drag:
                self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
                self.move(
                    event.x() + self.x() - self.posX, event.y() + self.y() - self.posY
                )
