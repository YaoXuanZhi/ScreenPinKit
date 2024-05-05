# coding=utf-8
import win32ui, win32con
import typing, os, threading
from datetime import datetime
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qfluentwidgets import (RoundMenu, Action, FluentIcon, StateToolTip)
from painter_tools import QDragWindow, QPainterWidget, DrawActionEnum
from canvas_item.canvas_util import ZoomComponent
from canvas_item import *
from ocr_service import *

class FreezerWindow(QDragWindow):  # 固定图片类
    ocrStartSignal = pyqtSignal()
    ocrEndSignal = pyqtSignal(list, list, list)
    def __init__(self, parent, screenPoint:QPoint, physicalSize:QSize, physicalPixmap:QPixmap, closeCallback:typing.Callable):
        super().__init__(parent)
        self.contentLayout = QVBoxLayout(self)
        self.shadowWidth = 30
        self.xRadius = 20
        self.yRadius = 20
        self.borderLineWidth = 0.5
        self.physicalPixmap = physicalPixmap
        self.setGeometry(screenPoint.x()-self.shadowWidth, screenPoint.y()-self.shadowWidth, physicalSize.width()+2*self.shadowWidth, physicalSize.height()+2*self.shadowWidth)
        self.contentLayout.setContentsMargins(self.shadowWidth, self.shadowWidth, self.shadowWidth, self.shadowWidth)

        self.painterWidget = QPainterWidget(self, physicalPixmap, self.xRadius, self.yRadius)
        self.contentLayout.addWidget(self.painterWidget)

        self.zoomComponent = ZoomComponent()
        self.zoomComponent.signal.connect(self.zoomHandle)

        self.defaultFlag()
        self.initActions()
        self.initBlink()

        self.unFocusColor = QColor(125, 125, 125, 50)
        self.focusColor = QColor(255, 0, 255, 50)
        self.focused = False
        self.painter = QPainter()
        self.closeCallback = closeCallback
        self.painterWidget.initDrawLayer()
        self.painterWidget.drawWidget.setEditorEnabled(False)
        self.show()

    def zoomHandle(self, zoomFactor):
        finalValue = self.windowOpacity()
        if zoomFactor > 1:
            finalValue = finalValue + 0.1
        else:
            finalValue = finalValue - 0.1

        finalValue = min(max(0.2, finalValue), 1)

        self.setWindowOpacity(finalValue)

    def defaultFlag(self):
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

    def initActions(self):
        actions = [
            Action("复制贴图", self, triggered=self.copyToClipboard, shortcut="ctrl+c"),
            Action("保存贴图", self, triggered=self.saveToDisk, shortcut="ctrl+s"),
            Action("开始OCR", self, triggered=self.startOcr, shortcut="ctrl+a"),
        ]
        self.addActions(actions)

        self.ocrStartSignal.connect(self.onBeginCallBack)
        self.ocrEndSignal.connect(self.onEndCallBack)

    def startOcr(self):
        '''使用独立线程进行OCR识别'''
        if hasattr(self, "ocrState"):
            return
        self.ocrState = 0
        self.ocrThread = OcrThread(self.onExecuteOcr, self.physicalPixmap)
        self.ocrThread.start()

    def onExecuteOcr(self, pixmap:QPixmap):
        print(f"ocr info [{OcrService.isSupported()}]: {pixmap.size()} {os.getppid()} {threading.current_thread().ident}")
        ocrService = OcrService()
        self.ocrStartSignal.emit()
        # boxes, txts, scores = ocrService.ocr(pixmap)
        boxes, txts, scores = ocrService.ocrWithProcess(pixmap)
        self.ocrEndSignal.emit(boxes, txts, scores)
        self.ocrState = 1

    def onBeginCallBack(self):
        if not hasattr(self, "stateTooltip") or self.stateTooltip == None:
            self.stateTooltip = StateToolTip('正在OCR识别', '客官请耐心等待哦~~', self)
            self.stateTooltip.setStyleSheet("background: transparent; border:0px;")
            self.stateTooltip.move(self.painterWidget.frameRect().topRight() + QPoint(-self.stateTooltip.frameSize().width(), self.stateTooltip.frameSize().height()))
            self.stateTooltip.show()

    def onEndCallBack(self, boxes, txts, scores):
        if hasattr(self, "stateTooltip") and self.stateTooltip != None:
            self.stateTooltip.setContent('OCR识别已结束')
            self.stateTooltip.setState(True)
            self.stateTooltip = None
        drop_score = 0.5
        for idx, (box, txt) in enumerate(zip(boxes, txts)):
            if scores is not None and scores[idx] < drop_score:
                continue
            
            box = np.reshape(np.array(box), [-1, 1, 2]).astype(np.int64)

            polygon = QPolygonF()
            for tuple in box:
                finalPosition = self.painterWidget.drawWidget.view.mapToScene(QPointF(tuple[0][0], tuple[0][1]).toPoint())
                polygon.append(finalPosition)

            textItem = CanvasOcrTextItem(polygon.boundingRect(), txt)
            self.painterWidget.drawWidget.scene.addItem(textItem)
            self.painterWidget.drawWidget.scene.addPolygon(polygon, QPen(Qt.GlobalColor.yellow), QBrush(Qt.NoBrush))

        if hasattr(self, "ocrThread"):
            self.ocrThread.quit()
            self.ocrThread = None

    def copyToClipboard(self):
        # 因为Windows下剪贴板不支持透明度，其会将Image里的alpha值用255直接进行填充，相关讨论可以看下面这两个链接
        # https://stackoverflow.com/questions/44177115/copying-from-and-to-clipboard-loses-image-transparency/46424800#46424800
        # https://stackoverflow.com/questions/44287407/text-erased-from-screenshot-after-using-clipboard-getimage-on-windows-10/46400011#46400011

        # self.pixmapWidget.copyToClipboard()
        finalPixmap = self.grab()
        QApplication.clipboard().setPixmap(finalPixmap)

    def saveToDisk(self):
        # 获取当前时间，并格式化
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        fileName = f"Snipaste_{now_str}.png"
        savePath, _ = QFileDialog.getSaveFileName(self, "Save File", f"./{fileName}", "PNG(*.png)")
        # 检查用户是否点击了“取消”
        if savePath != None:
            # 保存的截图无阴影
            # finalPixmap = self.pixmapWidget.getFinalPixmap()

            # 保存带阴影的截图
            finalPixmap = self.grab()
            finalPixmap.save(savePath, "png")

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

    def isAllowDrag(self):
        if self.painterWidget.drawWidget != None:
            return not self.painterWidget.drawWidget.isEditorEnabled()
        return True

    def isAllowModifyOpactity(self):
        return self.isAllowDrag()

    def mousePressEvent(self, event):
        self.isPresse = True
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.isPresse = False
        return super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            if self.isAllowDrag():
                self.close()

    # def showEvent(self, event: QShowEvent):
    #     self.startOcr()
    #     return super().showEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self.isAllowModifyOpactity() and int(event.modifiers()) == Qt.ControlModifier:
            self.zoomComponent.TriggerEvent(event.angleDelta().y())
            return
        else:
            return super().wheelEvent(event)

    def initBlink(self):
        self.blinkColors = [Qt.GlobalColor.red, Qt.GlobalColor.yellow, Qt.GlobalColor.green]
        self.blinkTimers = 0
        self.blinkColor = self.blinkColors[self.blinkTimers]

        self.blinkTimer = QtCore.QTimer(self)
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
            # i_path.addRect(ref)
            i_path.addRoundedRect(ref, self.xRadius, self.yRadius)
            color.setAlpha(int(150 - i**0.5*50))
            # color.setAlpha(int(150 - math.sqrt(i) * 50))
            self.painter.setPen(color)
            self.painter.drawPath(i_path)

        # 绘制闪烁边框
        if self.blinkColor != None:
            blinkPen = QPen(self.blinkColor)  # 实线，浅蓝色
            blinkPen.setStyle(QtCore.Qt.PenStyle.SolidLine)  # 实线SolidLine，虚线DashLine，点线DotLine
            blinkPen.setWidthF(self.borderLineWidth)  # 0表示线宽为1
            self.painter.setPen(blinkPen)
            rect = self.painterWidget.geometry()
            # self.painter.drawRect(rect)
            self.painter.drawRoundedRect(rect, self.xRadius, self.yRadius)

        self.painter.end()

    def closeEvent(self, event) -> None:
        self.painterWidget.close()
        if self.closeCallback != None:
            self.closeCallback()