from .canvas_util import *

class CanvasMarkerItem(QGraphicsRectItem):
    '''
    绘图工具-索引标识
    @note 滚轮可以改变索引值
    '''
    markderIndex = 0
    def __init__(self, rect: QRectF, parent:QGraphicsItem = None) -> None:
        super().__init__(rect, parent)
        self.__initStyle()
        self.setDefaultFlag()
        CanvasMarkerItem.markderIndex = self.markderIndex + 1
        self.index = CanvasMarkerItem.markderIndex
        self.transformComponent = TransformComponent()

    def __initStyle(self):
        styleMap = {
            "font" : QFont(),
            "textColor" : QColor(Qt.GlobalColor.red),
            "backgroundColor" : QColor(0, 255, 0, 150),
        }
        self.styleAttribute = CanvasAttribute()
        self.styleAttribute.setValue(QVariant(styleMap))
        self.styleAttribute.valueChangedSignal.connect(self.styleAttributeChanged)

    def type(self) -> int:
        return EnumCanvasItemType.CanvasMarkerItem.value

    @property
    def showText(self): return f"{self.index}"

    def styleAttributeChanged(self):
        self.update()

    def resetStyle(self, styleMap):
        self.styleAttribute.setValue(QVariant(styleMap))

    # 设置默认模式
    def setDefaultFlag(self):
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
        styleMap = self.styleAttribute.getValue().value()
        font = styleMap["font"]
        textColor = styleMap["textColor"]
        backgroundColor = styleMap["backgroundColor"]

        painter.save()
        painter.setBrush(backgroundColor)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.boundingRect())

        painter.setPen(textColor)

        offset = 5
        tempRect2 = self.boundingRect() - QMarginsF(offset, offset, offset, offset)
        CanvasUtil.adjustFontSizeToFit(self.showText, font, tempRect2, 1, 100)
        painter.setFont(font)

        align = Qt.AlignHCenter | Qt.AlignVCenter
        painter.drawText(self.rect(), align, self.showText)

        painter.restore()

    def setEditableState(self, isEditable:bool):
        '''设置可编辑状态'''
        self.setFlag(QGraphicsItem.ItemIsMovable, isEditable)
        self.setFlag(QGraphicsItem.ItemIsSelectable, isEditable)
        self.setFlag(QGraphicsItem.ItemIsFocusable, isEditable)
        self.setAcceptHoverEvents(isEditable)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.oldPos = self.pos()
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self.pos() != self.oldPos:
            self.transformComponent.movedSignal.emit(self, self.oldPos, self.pos())
        return super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        finalIndex = self.index
        if event.delta() > 0:
            finalIndex = finalIndex + 1
        else:
            finalIndex = max(1, finalIndex - 1)

        self.index = finalIndex
        self.update()

    def completeDraw(self):
        pass