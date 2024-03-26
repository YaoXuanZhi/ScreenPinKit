import sys, math
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPaintEvent, QPainter
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class UICanvasTextItem(QGraphicsTextItem):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        font = QFont()
        font.setPointSize(20)
        self.setFont(font)

        self.setDefaultFlag()
        self.setDefaultTextColor(Qt.white)

    # 设置默认模式
    def setDefaultFlag(self):
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

    # 取消文本选中状态
    def cancelSelectedText(self):
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)

    def isCanEditable(self):
        '''判断窗口的鼠标是否穿透了'''
        return (self.textInteractionFlags() | Qt.TextEditorInteraction) == self.textInteractionFlags()

    def switchEditableBox(self):
        self.clearFocus()
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.setFocus()

        textCursor = self.textCursor()
        pos = math.ceil(len(self.toPlainText())/2)
        textCursor.setPosition(pos)
        self.setTextCursor(textCursor)

    def focusInEvent(self, event: QFocusEvent) -> None:
        if (event.reason() != Qt.PopupFocusReason): # 注意右键菜单在此进入焦点时不保存原始文本
            self.m_store_str = self.toPlainText() # 保存原始文本
        return super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        if(event.reason() == Qt.MouseFocusReason and QApplication.mouseButtons()== Qt.RightButton):
            # 右键点击其他地方失去焦点，定义为取消操作，恢复原始文本
            self.setPlainText(self.m_store_str)
            self.setTextInteractionFlags(Qt.NoTextInteraction) # 恢复不能编辑状态
        elif(event.reason() == Qt.PopupFocusReason):
            #右键弹出菜单时不做处理
            pass
        else:
            #其他情况，包括下面点击回车的情况，编辑成功，发送信号给父对象
            self.cancelSelectedText()
            self.setDefaultFlag()
            # self.mySignal.emit(self.toPlainText())
        return super().focusOutEvent(event)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if(event.button() == Qt.LeftButton):
            if not self.isCanEditable():
                # 左键双击进入可编辑状态并打开焦点
                self.switchEditableBox()

        super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        # 自定义滚轮事件的行为
        finalFont = self.font()
        finalFontSize = finalFont.pointSize()
        # 例如，你可以改变文本的大小
        if event.angleDelta().y() > 0:
            # 放大
            finalFontSize = finalFontSize + 1
        else:
            # 缩小
            finalFontSize = finalFontSize - 1
        finalFont.setPointSize(finalFontSize)
        self.setFont(finalFont)
        self.update()

class CanvasScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initNodes()

    def initNodes(self):
        rectItem = QGraphicsRectItem(QRectF(-100, -100, 100, 100))
        rectItem.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        rectItem.setAcceptHoverEvents(True)
        self.addItem(rectItem)

        textItem = UICanvasTextItem()
        textItem.setPlainText("测试文本")
        textItem.switchEditableBox()
        self.addItem(textItem)

class CanvasView(QGraphicsView):
    def __init__(self, scene:QGraphicsScene, parent=None):
        super().__init__(scene, parent)

        self.initUI()

        self.zoomInFactor = 1.25
        self.zoomClamp = False # 是否限制缩放比率
        self.zoom = 10
        self.zoomStep = 1
        self.zoomRange = [0, 10]

    def initUI(self):
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.scene_width, self.scene_height = 64000, 64000
        self.scene().setSceneRect(-self.scene_width//2, -self.scene_height//2, self.scene_width, self.scene_height)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def wheelEvent(self, event:QWheelEvent):
        # 检查滚轮事件是否在 UICanvasTextItem 上发生
        item = self.itemAt(event.pos())
        if item and isinstance(item, UICanvasTextItem):
            item.wheelEvent(event)
            # 接受事件，防止它被传递到其他处理器
            event.accept()
        else:
            # 如果不是在 QGraphicsTextItem 上，调用默认的处理方法
            self.wheelEventView(event)

    def wheelEventView(self, event):
        # calculate our zoom Factor
        zoomOutFactor = 1 / self.zoomInFactor

        # calculate zoom
        if event.angleDelta().y() > 0:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep

        clamped = False
        if self.zoom < self.zoomRange[0]: self.zoom, clamped = self.zoomRange[0], True
        if self.zoom > self.zoomRange[1]: self.zoom, clamped = self.zoomRange[1], True

        # set scene scale
        if not clamped or self.zoomClamp is False:
            self.scale(zoomFactor, zoomFactor)

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.show()

    def initUI(self):
        self.setStyleSheet("QWidget { background-color: #E3212121; }")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.scene = CanvasScene()
        view = CanvasView(self.scene)
        self.layout.addWidget(view)

    def paintEvent(self, a0: QPaintEvent) -> None:
        backgroundPath = QPainterPath()
        backgroundPath.setFillRule(Qt.WindingFill)

        return super().paintEvent(a0)

if __name__ == '__main__':
    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    # app.setQuitOnLastWindowClosed(False)

    wnd = MainWindow()

    sys.exit(app.exec_())