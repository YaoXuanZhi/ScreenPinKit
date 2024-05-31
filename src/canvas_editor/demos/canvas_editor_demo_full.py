import sys, os
from enum import Enum
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

sys.path.insert(0, os.path.join( os.path.dirname(__file__), "..", ".." ))

from canvas_item import *
from canvas_editor import *
from base import *

class MainWindow(DragWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.defaultFlag()
        self.initUI()
        self.initActions()
        self.initSystemTrayMenu()
        self.show()
        self.painter = QPainter()
        self.focusColor = QColor(255, 0, 255, 50)

    def defaultFlag(self):
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

    def initSystemTrayMenu(self):
        self.systemTrayIcon = QSystemTrayIcon()

        trayPixmap = QPixmap(16, 16)
        trayPixmap.fill(QColor(100, 100, 100))
        self.systemTrayIcon.setIcon(QIcon(trayPixmap))
        self.systemTrayIcon.setToolTip("CanvasEditorDemo")
        self.systemTrayIcon.show()

        contextMenu = QMenu(self)
        trayMenuActions = [
            QAction('退出', self, triggered=self.exit),
            QAction('绘画模式', self, triggered=self.startDraw),
        ]
        contextMenu.addActions(trayMenuActions)
        self.systemTrayIcon.setContextMenu(contextMenu)

    def exit(self):
        sys.exit(0)

    def removeMouseThougth(self):
        self.setMouseThroughState(False)

    def initActions(self):
        finalDrawActions = [
            QAction("退出", self, triggered=self.quitDraw, shortcut="esc"),
            QAction("切换到演示模式", self, triggered=self.swtichShow, shortcut="ctrl+w"),
            QAction("切换到绘画模式", self, triggered=self.startDraw, shortcut="ctrl+t"),
            QAction("切换锁定状态", self, triggered=lambda: self.canvasEditor.switchLockState(), shortcut="alt+0"),

            QAction("切换到铅笔", self, triggered=lambda: self.switchDrawTool(DrawActionEnum.UsePencil), shortcut="alt+1"),
            QAction("切换到折线", self, triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawLineStrip), shortcut="alt+2"),
            QAction("绘制多边形", self, triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawShape), shortcut="alt+3"),
            QAction("绘制箭头", self, triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawArrow), shortcut="alt+4"),
            QAction("切换到选择工具", self, triggered=lambda: self.switchDrawTool(DrawActionEnum.SelectItem), shortcut="alt+7"),
        ]

        # 仅当有背景画刷的时候，橡皮擦和模糊工具才可以使用
        if not self.physicalPixmap.isNull():
            extendActions = [
                QAction('橡皮擦', self, triggered=lambda: self.switchDrawTool(DrawActionEnum.UseEraser), shortcut="alt+5"),
                QAction('橡皮框', self, triggered=lambda: self.switchDrawTool(DrawActionEnum.UseEraserRectItem), shortcut="alt+6"),
            ]
            for action in extendActions:
                finalDrawActions.append(action)

        self.addActions(finalDrawActions)

    def quitDraw(self):
        if self.canvasEditor.isEditorEnabled():
            self.canvasEditor.quitDraw()
        else:
            sys.exit(0)

    def swtichShow(self):
        self.canvasEditor.setEditorEnabled(False)
        self.setMouseThroughState(True)

    def startDraw(self):
        self.canvasEditor.setEditorEnabled(True)
        self.setMouseThroughState(False)

    def switchDrawTool(self, drawActionEnum:DrawActionEnum):
        self.canvasEditor.switchDrawTool(drawActionEnum)

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

    def initUI(self):
        self.contentLayout = QVBoxLayout(self)
        self.shadowWidth = 10
        sceneBrush = None

        # 桌面标注模式
        self.physicalPixmap = QPixmap()

        # 截图标注模式
        imagePath = os.path.join(os.path.dirname(__file__), "screen 451-180.png")
        self.physicalPixmap = QPixmap(imagePath)

        finalPixmap, finalGeometry = canvas_util.CanvasUtil.grabScreens()
        if self.physicalPixmap.isNull():
            self.screenPixmap = finalPixmap
            self.setGeometry(finalGeometry)
            self.contentLayout.setContentsMargins(0, 0, 0, 0)
        else:
            # 计算得到高分辨率缩放下最终尺寸
            screenDevicePixelRatio = QApplication.primaryScreen().grabWindow(0).devicePixelRatio()
            self.physicalPixmap.setDevicePixelRatio(screenDevicePixelRatio)
            realSize:QSizeF = self.physicalPixmap.size() / screenDevicePixelRatio

            screenPoint = finalGeometry.center() / 2
            self.setGeometry(screenPoint.x()-self.shadowWidth, screenPoint.y()-self.shadowWidth, realSize.width()+2*self.shadowWidth, realSize.height()+2*self.shadowWidth)
            self.contentLayout.setContentsMargins(self.shadowWidth, self.shadowWidth, self.shadowWidth, self.shadowWidth)

            sceneBrush = QBrush(self.physicalPixmap)
            transform = QtGui.QTransform()
            transform.scale(1/screenDevicePixelRatio, 1/screenDevicePixelRatio)
            sceneBrush.setTransform(transform)
        self.canvasEditor = CanvasEditor(None, sceneBrush)
        self.canvasEditor.initUI()
        self.contentLayout.addWidget(self.canvasEditor)
        self.canvasEditor.scene.initNodes()

    def isAllowDrag(self):
        if self.physicalPixmap.isNull():
            return False
        return not self.canvasEditor.isEditorEnabled()

    def paintEvent(self, a0: QPaintEvent) -> None:
        if self.physicalPixmap.isNull():
            return super().paintEvent(a0)

        self.painter.begin(self)
        self.painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 抗锯齿

    	# 阴影
        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        self.painter.fillPath(path, QBrush(Qt.white))
        color = self.focusColor

        for i in range(10):
            i_path = QPainterPath()
            i_path.setFillRule(Qt.WindingFill)
            ref = QRectF(self.shadowWidth-i, self.shadowWidth-i, self.width()-(self.shadowWidth-i)*2, self.height()-(self.shadowWidth-i)*2)
            # i_path.addRect(ref)
            i_path.addRoundedRect(ref, 5, 5)
            color.setAlpha(int(150 - i**0.5*50))
            # color.setAlpha(150 - math.sqrt(i) * 50)
            self.painter.setPen(color)
            self.painter.drawPath(i_path)

        self.painter.end()

        self.painter.begin(self)
        frameRect:QRectF = self.rect() - QMargins(self.shadowWidth, self.shadowWidth, self.shadowWidth, self.shadowWidth)
        self.painter.drawPixmap(frameRect, self.physicalPixmap)
        self.painter.end()

if __name__ == '__main__':
    import sys
    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    # app.setQuitOnLastWindowClosed(False)

    wnd = MainWindow()

    sys.exit(app.exec_())