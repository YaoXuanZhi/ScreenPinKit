# coding=utf-8
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtGui import QShowEvent
from PyQt5.QtWidgets import *
from .drag_window import *
from .shadow_window import *

class PinWindow(DragWindow):
    def __init__(self, parent, screenPoint:QPoint, physicalSize:QSize, physicalPixmap:QPixmap, closeCallback:typing.Callable):
        super().__init__(parent)
        self.shadowWidth = 10
        self.roundRadius = 20
        self.physicalPixmap = physicalPixmap
        self.setGeometry(screenPoint.x(), screenPoint.y(), physicalSize.width(), physicalSize.height())

        self.defaultFlag()

        self.closeCallback = closeCallback
        self.painter = QPainter()

        self.show()
        self.shadowWindow = ShadowWindow(self.roundRadius, self.shadowWidth, self)

    def defaultFlag(self) -> None:
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)

    def setRoundRadius(self, value):
        self.shadowWindow.setRoundRadius(value)
        self.roundRadius = value
        self.update()

    def setShadowColor(self, focusColor:QColor, unFocusColor:QColor):
        self.shadowWindow.setShadowColor(focusColor, unFocusColor)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.isAllowDrag():
                self.close()

    def isAllowDrag(self):
        return True

    def paintEvent(self, event):
        self.painter.begin(self)
        self.painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 抗锯齿

        if self.roundRadius > 0:
            clipPath = QPainterPath()
            clipPath.addRoundedRect(QRectF(self.rect()), self.roundRadius, self.roundRadius)
            self.painter.setClipPath(clipPath)
        self.painter.drawPixmap(0, 0, self.physicalPixmap)

        self.painter.end()

    def closeEvent(self, event) -> None:
        self.shadowWindow.close()
        if self.closeCallback != None:
            self.closeCallback()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Left:
            self.move(self.x() - 1, self.y())
        elif event.key() == Qt.Key_Right:
            self.move(self.x() + 1, self.y())
        elif event.key() == Qt.Key_Up:
            self.move(self.x(), self.y() - 1)
        elif event.key() == Qt.Key_Down:
            self.move(self.x(), self.y() + 1)

    def focusInEvent(self, event:QFocusEvent) -> None:
        self.shadowWindow.focusInEvent(event)

    def focusOutEvent(self, event:QFocusEvent) -> None:
        self.shadowWindow.focusOutEvent(event)

    def setWindowOpacity(self, level: float) -> None:
        self.shadowWindow.setWindowOpacity(level)
        super().setWindowOpacity(level)  

    def grabWithShaodw(self) -> QPixmap:
        basePixmap = self.shadowWindow.grab()
        painter = QPainter()
        painter.begin(basePixmap)
        painter.drawPixmap(self.shadowWidth, self.shadowWidth, self.grab())
        painter.end()
        return basePixmap