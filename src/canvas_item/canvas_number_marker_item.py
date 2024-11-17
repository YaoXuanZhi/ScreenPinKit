# coding=utf-8
from .canvas_util import *


class CanvasNumberMarkerItem(QGraphicsRectItem):
    """
    绘图工具-索引标识
    @note 滚轮可以改变索引值
    """

    markderIndex = 0

    def __init__(self, rect: QRectF, parent: QGraphicsItem = None) -> None:
        super().__init__(rect, parent)
        self.__initStyle()
        self.setDefaultFlag()
        CanvasNumberMarkerItem.markderIndex = self.markderIndex + 1
        self.index = CanvasNumberMarkerItem.markderIndex
        self.transformComponent = TransformComponent()
        self.applyShadow()

    def applyShadow(self):
        shadowEffect = QGraphicsDropShadowEffect()
        shadowEffect.setBlurRadius(20)  # 阴影的模糊半径
        shadowEffect.setColor(QColor(0, 0, 0, 100))  # 阴影的颜色和透明度
        shadowEffect.setOffset(5, 5)  # 阴影的偏移量
        self.setGraphicsEffect(shadowEffect)

    def __initStyle(self):
        defaultFont = QFont()
        styleMap = {
            "font": defaultFont,
            "textColor": QColor(Qt.GlobalColor.white),
            "penColor": QColor(Qt.GlobalColor.red),
            "penWidth": 2,
            "penStyle": Qt.PenStyle.SolidLine,
            "brushColor": QColor(Qt.GlobalColor.red),
        }

        self.usePen = QPen()
        self.usePen.setWidth(styleMap["penWidth"])
        self.usePen.setColor(styleMap["penColor"])
        self.usePen.setStyle(styleMap["penStyle"])
        self.useBrushColor = styleMap["brushColor"]
        self.styleAttribute = CanvasAttribute()
        self.styleAttribute.setValue(QVariant(styleMap))
        self.styleAttribute.valueChangedSignal.connect(self.styleAttributeChanged)

    def type(self) -> int:
        return EnumCanvasItemType.CanvasMarkerItem.value

    @property
    def showText(self):
        return f"{self.index}"

    def styleAttributeChanged(self):
        styleMap = self.styleAttribute.getValue().value()
        penColor = styleMap["penColor"]
        penWidth = styleMap["penWidth"]
        penStyle = styleMap["penStyle"]
        self.usePen.setColor(penColor)
        self.usePen.setWidth(penWidth)
        self.usePen.setStyle(penStyle)

        self.useBrushColor = styleMap["brushColor"]

        self.update()

    def resetStyle(self, styleMap):
        self.styleAttribute.setValue(QVariant(styleMap))

    # 设置默认模式
    def setDefaultFlag(self):
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

    def paint(
        self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget
    ):
        styleMap = self.styleAttribute.getValue().value()
        font = styleMap["font"]
        textColor = styleMap["textColor"]

        painter.save()
        painter.setBrush(self.useBrushColor)
        painter.setPen(self.usePen)
        painter.drawEllipse(self.boundingRect())

        painter.setPen(textColor)

        offset = 5
        tempRect2 = self.boundingRect() - QMarginsF(offset, offset, offset, offset)
        CanvasUtil.adjustFontSizeToFit(self.showText, font, tempRect2, 1, 100)
        painter.setFont(font)

        align = Qt.AlignHCenter | Qt.AlignVCenter
        painter.drawText(self.rect(), align, self.showText)

        painter.restore()

    def setEditableState(self, isEditable: bool):
        """设置可编辑状态"""
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
        if int(event.modifiers()) == Qt.ControlModifier:
            finalIndex = self.index
            if event.delta() > 0:
                finalIndex = finalIndex + 1
            else:
                finalIndex = max(1, finalIndex - 1)
            self.index = finalIndex
            self.update()
            return
        else:
            finalStyleMap = self.styleAttribute.getValue().value()
            finalWidth = finalStyleMap["penWidth"]
            if event.delta() > 0:
                finalWidth = finalWidth + 1
            else:
                finalWidth = max(finalWidth - 1, 1)
            finalStyleMap["penWidth"] = finalWidth
            self.usePen.setWidth(finalWidth)
            self.styleAttribute.setValue(QVariant(finalStyleMap))

    def completeDraw(self):
        pass
