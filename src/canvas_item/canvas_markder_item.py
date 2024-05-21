from .canvas_util import *

class CanvasMarkderItem(QGraphicsRectItem):
    markderIndex = 0
    def __init__(self, rect: QRectF, parent:QGraphicsItem = None) -> None:
        super().__init__(rect, parent)
        self.__initStyle()
        self.setDefaultFlag()
        CanvasMarkderItem.markderIndex = self.markderIndex + 1
        self.showText = f"{self.markderIndex}"

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

    def completeDraw(self):
        pass