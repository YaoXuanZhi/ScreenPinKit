import sys, math
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QMouseEvent, QPaintEvent, QPainter
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QGraphicsSceneDragDropEvent, QGraphicsSceneMouseEvent, QGraphicsSceneWheelEvent, QStyleOptionGraphicsItem, QWidget
from PyQt5.QtSvg import QSvgWidget

class UICanvasMarkderItem(QGraphicsRectItem):
    markderIndex = 0
    def __init__(self, rect: QRectF, parent:QGraphicsItem = None) -> None:
        super().__init__(rect, parent)
        self.showText = ""
        self.setDefaultFlag()
        UICanvasMarkderItem.markderIndex = self.markderIndex + 1
        self.showText = f"{self.markderIndex}"

    # 设置默认模式
    def setDefaultFlag(self):
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        painter.save()
        painter.setBrush(QBrush(QColor(255, 255, 0, 50)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.boundingRect())

        painter.setPen(QColor(255, 255, 255))

        offset = 5
        tempRect2 = self.boundingRect() - QMarginsF(offset, offset, offset, offset)
        self.font = QFont()
        self.adjustFontSizeToFit(self.showText, self.font, tempRect2, 1, 100)
        painter.setFont(self.font)

        align = Qt.AlignHCenter | Qt.AlignVCenter
        painter.drawText(self.rect(), align, self.showText)

        painter.restore()

    def adjustFontSizeToFit(self, text, font:QFont, rect:QRectF, minFontSize = 1, maxFontSize = 50):
        '''调整字体适应大小'''

        # 计算给定字体大小下的文本宽度和高度
        def calcFontSize(targetFont):
            font_metrics = QFontMetricsF(targetFont)
            return font_metrics.size(0, text)

        finalFontSize = minFontSize
        while finalFontSize >= minFontSize and finalFontSize < maxFontSize:
            # 获取当前字体大小下的文本尺寸
            size = calcFontSize(QFont(font.family(), finalFontSize))
            if size.width() <= rect.width() and size.height() <= rect.height():
                # 如果文本可以放入矩形区域内，尝试使用更大的字体大小
                finalFontSize += 1
            else:
                # 文本太大，无法放入矩形区域，跳出循环
                break

            font.setPointSize(finalFontSize)

class DrawingScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 绘制矩形图元
        rectItem = QGraphicsRectItem(QRectF(-100, -100, 100, 100))
        rectItem.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        rectItem.setAcceptHoverEvents(True)
        self.addItem(rectItem)

class DrawingView(QGraphicsView):
    def __init__(self, scene:QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.initUI()

    def initUI(self):
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.scene_width, self.scene_height = 64000, 64000
        self.scene().setSceneRect(-self.scene_width//2, -self.scene_height//2, self.scene_width, self.scene_height)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        # self.setDragMode(QGraphicsView.RubberBandDrag)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            if not self.isCanDrag():
                item = self.itemAt(event.pos())
                if item == None:
                    self.currentItem = UICanvasMarkderItem(QRectF(0, 0, 20, 20))

                    self.scene().addItem(self.currentItem)

                    targetPos = self.mapToScene(event.pos())
                    targetPos.setX(targetPos.x() - self.currentItem.boundingRect().width() / 2)
                    targetPos.setY(targetPos.y() - self.currentItem.boundingRect().height() / 2)
                    self.currentItem.setPos(targetPos)

        return super().mousePressEvent(event)

    def isCanDrag(self):
        '''判断当前是否可以拖曳图元'''
        matchMode = self.dragMode()
        return (matchMode | QGraphicsView.RubberBandDrag == matchMode)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if(event.button() == Qt.RightButton):
            self.setDragMode(QGraphicsView.RubberBandDrag)
        elif (event.button() == Qt.LeftButton):
            self.setDragMode(self.dragMode() & ~QGraphicsView.RubberBandDrag)
        return super().mouseDoubleClickEvent(event)

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.show()

    def initUI(self):
        self.setStyleSheet("QWidget { background-color: #E3212121; }")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.scene = DrawingScene()
        view = DrawingView(self.scene)
        self.layout.addWidget(view)

    def paintEvent(self, a0: QPaintEvent) -> None:
        backgroundPath = QPainterPath()
        backgroundPath.setFillRule(Qt.WindingFill)

        return super().paintEvent(a0)

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