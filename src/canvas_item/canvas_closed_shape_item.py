from .canvas_util import *

class CanvasClosedShapeEnum(Enum):
    Ellipse = "椭圆"
    Rectangle = "矩形"
    Star = "五角星"

class CanvasClosedShapeItem(CanvasCommonPathItem):
    '''
    绘图工具-闭合形状
    @note 滚轮可以控制描边宽度
    '''
    def __init__(self, parent: QWidget = None, shapeType:CanvasClosedShapeEnum = CanvasClosedShapeEnum.Rectangle) -> None:
        super().__init__(parent)
        self.__initEditMode()
        self.__initStyle(shapeType)

        self.zoomComponent = ZoomComponent()
        self.zoomComponent.zoomClamp = False
        self.zoomComponent.signal.connect(self.zoomHandle)

    def __initStyle(self, shapeType:CanvasClosedShapeEnum):
        #todo 后续可以借用这里面的配置类 qfluentwidgets\common\config.py
        styleMap = {
            "brush" : QBrush(QColor(255, 10, 10, 100)),
            "pen" : QPen(QColor(255, 100, 100), 2, Qt.SolidLine),
            "shape" : shapeType,
        }
        self.styleAttribute = CanvasAttribute()
        self.styleAttribute.setValue(QVariant(styleMap))
        self.styleAttribute.valueChangedSignal.connect(self.update)

    def type(self) -> int:
        return EnumCanvasItemType.CanvasClosedShapeItem.value

    def resetStyle(self, styleMap):
        self.styleAttribute.setValue(QVariant(styleMap))

    def __initEditMode(self):
        '''仅保Roi操作点'''
        # self.setEditMode(CanvasCommonPathItem.BorderEditableMode, False)
        self.setEditMode(CanvasCommonPathItem.RoiEditableMode, False)
        self.setEditMode(CanvasCommonPathItem.HitTestMode, False)
        self.setEditMode(CanvasCommonPathItem.AdvanceSelectMode, False)

    def zoomHandle(self, zoomFactor):
        oldStyleMap = self.styleAttribute.getValue().value()
        pen:QPen = oldStyleMap["pen"]
        finalWidth = pen.width()
        if zoomFactor > 1:
            finalWidth = finalWidth + 1
        else:
            finalWidth = max(0, finalWidth - 1)

        pen.setWidth(finalWidth)
        self.styleAttribute.setValue(QVariant(oldStyleMap))

    def customPaint(self, painter: QPainter, targetPath:QPainterPath) -> None:
        styleMap = self.styleAttribute.getValue().value()
        painter.setBrush(styleMap["brush"])
        painter.setPen(styleMap["pen"])
        painter.drawPath(targetPath)

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        self.zoomComponent.TriggerEvent(event.delta())

    def getStretchableRect(self) -> QRect:
        return self.polygon.boundingRect()

    def buildShapePath(self, targetPath:QPainterPath, targetPolygon:QPolygonF, isClosePath:bool):
        styleMap = self.styleAttribute.getValue().value()
        shapeType = styleMap["shape"]
        if shapeType == CanvasClosedShapeEnum.Ellipse:
            CanvasUtil.buildEllipsePath(targetPath, targetPolygon)
        elif shapeType == CanvasClosedShapeEnum.Rectangle:
            CanvasUtil.buildRectanglePath(targetPath, targetPolygon)
        elif shapeType == CanvasClosedShapeEnum.Star:
            CanvasUtil.buildStarPath(targetPath, targetPolygon)