# coding=utf-8
from base import *
from .painter_interface import *


class QScreenPainterWidget(PainterInterface):
    completeDrawAfterSignal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent, None)

    def getCommandBarPosition(self) -> BubbleTipTailPosition:
        return BubbleTipTailPosition.BOTTOM

    def contextMenuEvent(self, event: QContextMenuEvent):
        return

    def completeDraw(self):
        super().completeDraw()
        self.completeDrawAfterSignal.emit()


class ScreenPaintWindow(MouseThroughWindow):  # 屏幕窗口
    def __init__(self, parent=None):
        super().__init__(parent)
        self.defaultFlag()
        self.initUI()
        self.initActions()

    def defaultFlag(self):
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

    def initUI(self):
        self.contentLayout = QVBoxLayout(self)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        finalPixmap, finalGeometry = canvas_util.CanvasUtil.grabScreens()
        self.setGeometry(finalGeometry)

        self.canvasEditor = QScreenPainterWidget(self)
        self.canvasEditor.completeDrawAfterSignal.connect(self.onCompleteDrawAfter)
        self.contentLayout.addWidget(self.canvasEditor)

        self.zoomComponent = ZoomComponent()
        self.zoomComponent.signal.connect(self.zoomHandle)

    def onCompleteDrawAfter(self):
        self.setMouseThroughState(True)

    def showEvent(self, a0: QShowEvent) -> None:
        self.activateWindow()
        if (
            self.canvasEditor.drawWidget != None
            and not self.canvasEditor.drawWidget.isEditorEnabled()
        ):
            return

        self.delayTimer = QTimer(self)
        self.delayTimer.timeout.connect(self.onDelayCallBack)
        self.delayTimer.start(30)

    def onDelayCallBack(self):
        self.delayTimer.stop()

        self.canvasEditor.initDrawLayer()
        self.canvasEditor.showCommandBar()
        self.canvasEditor.selectItemAction.trigger()

    def zoomHandle(self, zoomFactor):
        finalValue = self.windowOpacity()
        if zoomFactor > 1:
            finalValue = finalValue + 0.1
        else:
            finalValue = finalValue - 0.1

        # 经测试，发现该数值小于0.5之后，透明部分会穿透，因此透明度范围设为[0.5, 1]
        finalValue = min(max(0.5, finalValue), 1)

        self.setWindowOpacity(finalValue)

    def initActions(self):
        actions = [
            QAction(self, triggered=self.switchPreviewMode, shortcut="ctrl+w"),
        ]
        self.addActions(actions)

    def switchPreviewMode(self):
        self.canvasEditor.completeDraw()

    def startDraw(self):
        self.canvasEditor.drawWidget.setEditorEnabled(True)
        self.setMouseThroughState(False)

    def isAllowModifyOpactity(self):
        return self.canvasEditor.currentDrawActionEnum in [
            DrawActionEnum.SelectItem,
            DrawActionEnum.DrawNone,
        ]

    def wheelEvent(self, event: QWheelEvent) -> None:
        if (
            self.isAllowModifyOpactity()
            and int(event.modifiers()) == Qt.ControlModifier
        ):
            self.zoomComponent.TriggerEvent(event.angleDelta().y())
            return
        else:
            return super().wheelEvent(event)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            self.canvasEditor.tryQuitDraw()
