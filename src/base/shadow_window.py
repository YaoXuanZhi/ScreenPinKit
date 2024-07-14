# coding=utf-8
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtGui import QShowEvent
from PyQt5.QtWidgets import *
from .mouse_through_window import *

class ShadowWindow(MouseThroughWindow):
    blinkStopSignal = pyqtSignal()
    def __init__(self, roundRadius:int, shadowWidth:float, parent:QWidget):
        super(ShadowWindow, self).__init__(parent)
        self.attachParent = parent
        self.roundRadius = roundRadius
        self.shadowWidth = shadowWidth
        self.borderLineWidth = 0.5
        self.unFocusColor = QColor(125, 125, 125, 50)
        self.focusColor = QColor(255, 0, 255, 50)
        self.focused = False

        # 根据吸附的窗口大小设置阴影窗口大小
        self.margins = QMargins(self.shadowWidth, self.shadowWidth, self.shadowWidth, self.shadowWidth)
        self.setGeometry(self.attachParent.geometry() + self.margins)

        self.defaultFlag()
        self.painter = QPainter()

        self.attachParent.installEventFilter(self)
        self.setMouseThroughState(True)
        self.initBlink()
        self.show()

    def eventFilter(self, obj, event: QEvent):
        if event.type() == QEvent.Type.Resize:
            self.setGeometry(self.attachParent.geometry() + self.margins)
        elif event.type() == QEvent.Type.Move:
            self.move(self.attachParent.geometry().topLeft() - QPoint(self.shadowWidth, self.shadowWidth))
        elif event.type() == QEvent.Type.FocusIn:
            self.focused = True
            self.update()
        elif event.type() == QEvent.Type.FocusOut:
            self.focused = False
            self.update()
        return super().eventFilter(obj, event)

    def defaultFlag(self):
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

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
            self.blinkStopSignal.emit()

    def setRoundRadius(self, value):
        self.roundRadius = value
        self.update()

    def setShadowColor(self, focusColor:QColor, unFocusColor:QColor):
        self.focusColor = focusColor
        self.unFocusColor = unFocusColor
        self.update()

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
            if self.roundRadius > 0:
                i_path.addRoundedRect(ref, self.roundRadius, self.roundRadius)
            else:
                i_path.addRect(ref)
            color.setAlpha(int(150 - i**0.5*50))
            self.painter.setPen(color)
            self.painter.drawPath(i_path)

        # 绘制闪烁边框
        if self.blinkColor != None:
            blinkPen = QPen(self.blinkColor)  # 实线，浅蓝色
            blinkPen.setStyle(Qt.PenStyle.SolidLine)  # 实线SolidLine，虚线DashLine，点线DotLine
            blinkPen.setWidthF(self.borderLineWidth)  # 0表示线宽为1
            self.painter.setPen(blinkPen)
            rect = QRect(0, 0, self.width(), self.height())
            rect = rect - self.margins
            if self.roundRadius > 0:
                self.painter.drawRoundedRect(rect, self.roundRadius, self.roundRadius)
            else:
                self.painter.drawRect(rect)

        self.painter.end()