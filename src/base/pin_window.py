# coding=utf-8
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .drag_window import *

class PinWindow(DragWindow):
    def __init__(self, parent, screenPoint:QPoint, physicalSize:QSize, physicalPixmap:QPixmap, closeCallback:typing.Callable):
        super().__init__(parent)
        self.shadowWidth = 30
        self.roundRadius = 20
        self.borderLineWidth = 1.5
        self.physicalPixmap = physicalPixmap
        self.setGeometry(screenPoint.x()-self.shadowWidth, screenPoint.y()-self.shadowWidth, physicalSize.width()+2*self.shadowWidth, physicalSize.height()+2*self.shadowWidth)
        self.contentRect = self.rect() - QMargins(self.shadowWidth, self.shadowWidth, self.shadowWidth, self.shadowWidth)

        self.defaultFlag()
        self.initBlink()

        self.closeCallback = closeCallback
        self.unFocusColor = QColor(125, 125, 125, 50)
        self.focusColor = QColor(255, 0, 255, 50)
        self.focused = False
        self.isUseRoundStyle = True
        self.painter = QPainter()
        self.show()

    def defaultFlag(self):
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)

    def setRoundStyle(self, isUse:bool):
        self.isUseRoundStyle = isUse
        self.update()

    def setShadowColor(self, focusColor:QColor, unFocusColor:QColor):
        self.focusColor = focusColor
        self.unFocusColor = unFocusColor
        self.update()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.isAllowDrag():
                self.close()

    def initBlink(self):
        self.blinkColors = [Qt.GlobalColor.red, Qt.GlobalColor.yellow, Qt.GlobalColor.green]
        self.blinkTimers = 0
        self.blinkColor = self.blinkColors[self.blinkTimers]

        self.blinkTimer = QTimer(self)
        self.blinkTimer.timeout.connect(self.onBlinkTimerTimeout)
        self.blinkTimer.start(300)

    def onBlinkTimerTimeout(self):
        if self.blinkTimers < len(self.blinkColors) - 1:
            self.blinkTimers += 1
            self.blinkColor = self.blinkColors[self.blinkTimers]
            self.update()
        else:
            self.blinkTimer.stop()
            self.blinkColor = None
            self.update()
            self.activateWindow()

    def isAllowDrag(self):
        return True

    def focusInEvent(self, event:QFocusEvent) -> None:
        self.focused = True
        self.update()

    def focusOutEvent(self, event:QFocusEvent) -> None:
        self.focused = False
        self.update()

    def paintEvent(self, event):
        self.painter.begin(self)
        self.painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 抗锯齿

    	# 阴影
        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        self.painter.fillPath(path, QBrush(Qt.white))
        if self.focused:
            color = self.focusColor
        else:
            color = self.unFocusColor

        for i in range(10):
            i_path = QPainterPath()
            i_path.setFillRule(Qt.WindingFill)
            ref = QRectF(self.shadowWidth-i, self.shadowWidth-i, self.width()-(self.shadowWidth-i)*2, self.height()-(self.shadowWidth-i)*2)
            if self.isUseRoundStyle:
                i_path.addRoundedRect(ref, self.roundRadius, self.roundRadius)
            else:
                i_path.addRect(ref)
            color.setAlpha(int(150 - i**0.5*50))
            # color.setAlpha(int(150 - math.sqrt(i) * 50))
            self.painter.setPen(color)
            self.painter.drawPath(i_path)

        if self.isUseRoundStyle:
            clipPath = QPainterPath()
            clipPath.addRoundedRect(QRectF(self.contentRect), self.roundRadius, self.roundRadius)
            self.painter.setClipPath(clipPath)
        self.painter.drawPixmap(self.shadowWidth, self.shadowWidth, self.physicalPixmap)

        # 绘制闪烁边框
        if self.blinkColor != None:
            blinkPen = QPen(self.blinkColor)  # 实线，浅蓝色
            blinkPen.setStyle(Qt.PenStyle.SolidLine)  # 实线SolidLine，虚线DashLine，点线DotLine
            blinkPen.setWidthF(self.borderLineWidth)  # 0表示线宽为1
            self.painter.setPen(blinkPen)
            if self.isUseRoundStyle:
                self.painter.drawRoundedRect(self.contentRect, self.roundRadius, self.roundRadius)
            else:
                self.painter.drawRect(self.contentRect)

        self.painter.end()

    def closeEvent(self, event) -> None:
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