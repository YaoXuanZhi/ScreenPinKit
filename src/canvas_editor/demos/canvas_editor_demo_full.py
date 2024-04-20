import sys, os
from enum import Enum
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

sys.path.insert(0, os.path.join( os.path.dirname(__file__), "..", ".." ))

from canvas_item import *
from canvas_editor import *

# 拖曳移动窗口类
class QDragWindow(QLabel):
    def __init__(self, parent:QWidget):
        super().__init__(parent)
        self.drag = False

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
                self.move(event.x() + self.x() - self.posX, event.y() + self.y() - self.posY)

class MainWindow(QDragWindow):
# class MainWindow(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.defaultFlag()
        self.initUI()
        self.initActions()
        self.show()
        self.painter = QPainter()
        self.focusColor = QColor(255, 0, 255, 50)

    def defaultFlag(self):
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)

    def initActions(self):
        actions = [
            QAction("退出", self, triggered=self.quitDraw, shortcut="esc"),
            QAction("切到画板但无操作", self, triggered=self.swtichOption, shortcut="ctrl+w"),
            QAction("切换到演示模式", self, triggered=self.swtichShow, shortcut="alt+w"),
            QAction("切到画板但无操作", self, triggered=self.startDraw, shortcut="ctrl+t"),
            QAction("切换到铅笔", self, triggered=lambda: self.switchDrawTool(DrawActionEnum.UsePencil), shortcut="alt+1"),
            QAction("切换到折线", self, triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawPolygonalLine), shortcut="alt+2"),
            QAction("切换到记号笔", self, triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawMarkerPen), shortcut="alt+3"),
            QAction("切换多选操作", self, triggered=self.switchCanvas, shortcut="alt+4"),
        ]
        self.addActions(actions)

    def quitDraw(self):
        if self.canvasEditor.isEditorEnabled():
            self.canvasEditor.quitDraw()
        else:
            sys.exit(0)

    def swtichOption(self):
        # color = QColor(Qt.GlobalColor.yellow)
        # color.setAlpha(1)
        # self.scene.setBackgroundBrush(QBrush(color))
        self.canvasEditor.setEditorEnabled(True)

    def swtichShow(self):
        # self.scene.setBackgroundBrush(QBrush(Qt.NoBrush))
        self.canvasEditor.setEditorEnabled(False)

    def startDraw(self):
        self.canvasEditor.setEditorEnabled(True)

    def switchCanvas(self):
        # self.view.switchCanvas()
        pass

    def switchDrawTool(self, drawActionEnum:DrawActionEnum):
        self.canvasEditor.switchDrawTool(drawActionEnum)

    def initUI(self):
        self.setStyleSheet("QWidget { background-color: #E3212121; }")
        self.contentLayout = QVBoxLayout(self)
        self.physicalPixmap = QPixmap("screen 143-313.png")
        self.shadowWidth = 20

        if self.physicalPixmap.isNull():
            finalPixmap, finalGeometry = canvas_util.CanvasUtil.grabScreens()
            self.screenPixmap = finalPixmap
            self.setGeometry(finalGeometry)
            self.contentLayout.setContentsMargins(0, 0, 0, 0)
        else:
            self.setPixmap(self.physicalPixmap)

            finalSize = self.physicalPixmap.size()
            finalSize.setWidth(finalSize.width() + self.shadowWidth)
            finalSize.setHeight(finalSize.height() + self.shadowWidth)
            self.resize(finalSize)
            self.contentLayout.setContentsMargins(self.shadowWidth, self.shadowWidth, self.shadowWidth, self.shadowWidth)

        self.canvasEditor = CanvasEditor()
        self.canvasEditor.initUI()
        self.contentLayout.addWidget(self.canvasEditor)
        self.canvasEditor.scene.initNodes()

    def isAllowDrag(self):
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
        frameRect = self.rect() - QMargins(self.shadowWidth, self.shadowWidth, self.shadowWidth, self.shadowWidth)
        self.painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        clipPath = QPainterPath()
        clipPath.addRoundedRect(QRectF(self.rect()), 5, 5)
        self.painter.setClipPath(clipPath)
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