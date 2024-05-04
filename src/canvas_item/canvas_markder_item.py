from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class CanvasMarkderItem(QGraphicsRectItem):
    markderIndex = 0
    def __init__(self, rect: QRectF, parent:QGraphicsItem = None) -> None:
        super().__init__(rect, parent)
        self.showText = ""
        self.setDefaultFlag()
        CanvasMarkderItem.markderIndex = self.markderIndex + 1
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

    # def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
    #     if event.button() == Qt.MouseButton.LeftButton:
    #         raise NotImplementedError("子类需要重写该函数")
    #         return
    #     return super().mouseDoubleClickEvent(event)

    def setEditableState(self, isEditable:bool):
        '''设置可编辑状态'''
        self.setFlag(QGraphicsItem.ItemIsMovable, isEditable)
        self.setFlag(QGraphicsItem.ItemIsSelectable, isEditable)
        self.setFlag(QGraphicsItem.ItemIsFocusable, isEditable)
        self.setAcceptHoverEvents(isEditable)

    def completeDraw(self):
        pass