# coding=utf-8
import typing, os, threading
from datetime import datetime
from qfluentwidgets import (RoundMenu, Action, StateToolTip)
from base import *
from canvas_item import *
from canvas_item.canvas_util import ZoomComponent
from canvas_editor import DrawActionEnum
from common import cfg, ScreenShotIcon
from ocr_service import *
from .painter_interface import PainterInterface

class PinEditorWindow(PinWindow):
    ocrStartSignal = pyqtSignal()
    ocrEndSignal = pyqtSignal(list, list, list)
    def __init__(self, parent, screenPoint:QPoint, physicalSize:QSize, physicalPixmap:QPixmap, closeCallback:typing.Callable):
        super().__init__(parent, screenPoint, physicalSize, physicalPixmap, closeCallback)
        self.contentLayout = QVBoxLayout(self)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.painterWidget = PainterInterface(self, physicalPixmap)
        self.contentLayout.addWidget(self.painterWidget)

        self.zoomComponent = ZoomComponent()
        self.zoomComponent.signal.connect(self.zoomHandle)

        self.painterWidget.initDrawLayer()
        self.painterWidget.drawWidget.setEditorEnabled(False)

        self.setShadowColor(cfg.get(cfg.windowShadowStyleFocusColor), cfg.get(cfg.windowShadowStyleUnFocusColor))

        self.initActions()

    def contextMenuEvent(self, event:QContextMenuEvent):
        if self.painterWidget.currentDrawActionEnum != DrawActionEnum.DrawNone:
            return
        menu = RoundMenu(parent=self)
        menu.addActions([
            Action(ScreenShotIcon.WHITE_BOARD, self.tr("Show toolbar"), triggered=self.showCommandBar),
            Action(ScreenShotIcon.COPY, self.tr("Copy"), triggered=self.copyToClipboard),
            Action(ScreenShotIcon.SAVE_AS, self.tr("Save as"), triggered=self.saveToDisk),
            Action(ScreenShotIcon.CLICK_THROUGH, self.tr("Mouse through"), triggered=self.clickThrough),
        ])
        menu.view.setIconSize(QSize(20, 20))
        menu.exec(event.globalPos())

    def defaultFlag(self) -> None:
        super().defaultFlag()
        self.roundRadius = cfg.get(cfg.windowShadowStyleRoundRadius)

    def showCommandBar(self):
        self.painterWidget.showCommandBar()

    def clickThrough(self):
        self.painterWidget.clickThrough()

    def initActions(self):
        actions = [
            QAction(self, triggered=self.copyToClipboard, shortcut="ctrl+c"),
            QAction(self, triggered=self.saveToDisk, shortcut="ctrl+s"),
            QAction(self, triggered=self.startOcr, shortcut="ctrl+a"),
            QAction(self, triggered=self.completeDraw, shortcut="ctrl+w"),
        ]
        self.addActions(actions)

        self.ocrStartSignal.connect(self.onOcrStart)
        self.ocrEndSignal.connect(self.onOcrEnd)
        self.shadowWindow.blinkStopSignal.connect(self.onBlinkStop)
        cfg.windowShadowStyleRoundRadius.valueChanged.connect(self.setRoundRadius)
        cfg.windowShadowStyleUnFocusColor.valueChanged.connect(self.refreshShadowColor)
        cfg.windowShadowStyleFocusColor.valueChanged.connect(self.refreshShadowColor)

    def refreshShadowColor(self, _):
        focusColor = cfg.get(cfg.windowShadowStyleFocusColor)
        unFocusColor = cfg.get(cfg.windowShadowStyleUnFocusColor)
        self.setShadowColor(focusColor, unFocusColor)

    def completeDraw(self):
        self.painterWidget.completeDraw()

    def zoomHandle(self, zoomFactor):
        finalValue = self.windowOpacity()
        if zoomFactor > 1:
            finalValue = finalValue + 0.1
        else:
            finalValue = finalValue - 0.1

        finalValue = min(max(0.2, finalValue), 1)

        self.setWindowOpacity(finalValue)

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

    def onOcrStart(self):
        if not hasattr(self, "stateTooltip") or self.stateTooltip == None:
            self.stateTooltip = StateToolTip('正在OCR识别', '客官请耐心等待哦~~', self)
            self.stateTooltip.setStyleSheet("background: transparent; border:0px;")
            self.stateTooltip.move(self.painterWidget.geometry().topRight() + QPoint(-self.stateTooltip.frameSize().width() - 20, self.stateTooltip.frameSize().height() - 20))
            self.stateTooltip.show()

    def onOcrEnd(self, boxes, txts, scores):
        if hasattr(self, "stateTooltip") and self.stateTooltip != None:
            self.stateTooltip.setContent('OCR识别已结束')
            self.stateTooltip.setState(True)
            self.stateTooltip = None

        drop_score = 0.5
        dpiScale = CanvasUtil.getDevicePixelRatio()

        for i in range(0, len(boxes)):
            txt = txts[i]
            box = boxes[i]
            if scores is not None and scores[i] < drop_score:
                continue

            polygon = QPolygonF()
            for position in box:
                achorPos = QPointF(position[0] / dpiScale, position[-1] / dpiScale).toPoint()
                # finalPosition = self.drawWidget.view.mapToScene(achorPos)
                finalPosition = achorPos
                polygon.append(finalPosition)

            textItem = CanvasOcrTextItem(polygon.boundingRect(), txt)
            self.painterWidget.drawWidget.scene.addItem(textItem)
            self.painterWidget.drawWidget.scene.addPolygon(polygon, QPen(Qt.GlobalColor.yellow), QBrush(Qt.NoBrush))

        if hasattr(self, "ocrThread"):
            self.ocrThread.quit()
            self.ocrThread = None

    def onBlinkStop(self):
        self.activateWindow()

    def copyToClipboard(self):
        # 因为Windows下剪贴板不支持透明度，其会将Image里的alpha值用255直接进行填充，相关讨论可以看下面这两个链接
        # https://stackoverflow.com/questions/44177115/copying-from-and-to-clipboard-loses-image-transparency/46424800#46424800
        # https://stackoverflow.com/questions/44287407/text-erased-from-screenshot-after-using-clipboard-getimage-on-windows-10/46400011#46400011

        if cfg.get(cfg.windowShadowStyleIsCopyWithShadow):
            finalPixmap = self.grabWithShaodw()
        else:
            finalPixmap = self.painterWidget.getFinalPixmap()
        QApplication.clipboard().setPixmap(finalPixmap)

    def saveToDisk(self):
        # 获取当前时间，并格式化
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        fileName = cfg.get(cfg.imageNameFormat) % (now_str)

        tempFolder = cfg.get(cfg.cacheFolder)
        finalFolder = "./"
        if os.path.exists(tempFolder):
            finalFolder = tempFolder
        finalPath = os.path.join(finalFolder, fileName)
        savePath, _ = QFileDialog.getSaveFileName(self, "Save File", finalPath, "PNG(*.png)")
        if savePath != None:
            if cfg.get(cfg.windowShadowStyleIsSaveWithShadow):
                finalPixmap = self.grabWithShaodw()
            else:
                finalPixmap = self.painterWidget.getFinalPixmap()
            finalPixmap.save(savePath, "png")

    def isAllowDrag(self):
        if self.painterWidget.drawWidget != None:
            return not self.painterWidget.drawWidget.isEditorEnabled()
        return True

    def isAllowModifyOpactity(self):
        return self.isAllowDrag()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.isAllowDrag():
                self.close()

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self.isAllowModifyOpactity() and int(event.modifiers()) == Qt.ControlModifier:
            self.zoomComponent.TriggerEvent(event.angleDelta().y())
            return
        else:
            return super().wheelEvent(event)

    def closeEvent(self, event) -> None:
        self.painterWidget.close()
        cfg.windowShadowStyleRoundRadius.valueChanged.disconnect(self.setRoundRadius)
        cfg.windowShadowStyleUnFocusColor.valueChanged.disconnect(self.refreshShadowColor)
        cfg.windowShadowStyleFocusColor.valueChanged.disconnect(self.refreshShadowColor)
        super().closeEvent(event)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            if self.painterWidget.tryQuitDraw():
                self.close()
        super().keyPressEvent(event)

    def setMouseThroughState(self, isThrough: bool):
        self.painterWidget.completeDraw()
        self.painterWidget.clearFocus()
        self.focusOutEvent(QFocusEvent(QEvent.Type.FocusOut, Qt.FocusReason.NoFocusReason))
        return super().setMouseThroughState(isThrough)