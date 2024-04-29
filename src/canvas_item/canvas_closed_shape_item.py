from .canvas_util import *

class CanvasClosedShapeEnum(Enum):
    Ellipse = "椭圆"
    Rectangle = "矩形"
    Star = "五角星"

class CanvasClosedShapeItem(CanvasCommonPathItem):
    '''
    绘图工具-闭合形状
    '''
    def __init__(self, parent: QWidget = None, shapeType:CanvasClosedShapeEnum = CanvasClosedShapeEnum.Rectangle) -> None:
        super().__init__(parent)
        self.__initEditMode()
        self.__initStyle()
        self.shapeType = shapeType

        self.zoomComponent = ZoomComponent()
        self.zoomComponent.zoomClamp = True
        self.zoomComponent.signal.connect(self.zoomHandle)

        # self.blur()

    def blur(self):
        """模糊"""
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(5)
        # blur.setBlurHints(QGraphicsBlurEffect.QualityHint)
        blur.setBlurHints(QGraphicsBlurEffect.PerformanceHint)
        self.setGraphicsEffect(blur)

    def __initStyle(self):
        styleMap = {
            "brush" : QBrush(QColor(255, 0, 0, 100)),
            "pen" : QPen(QColor(255, 0, 0), 2, Qt.SolidLine),
        }
        self.styleAttribute = CanvasAttribute()
        self.styleAttribute.setValue(QVariant(styleMap))
        self.styleAttribute.valueChangedSignal.connect(self.update)

    def __initEditMode(self):
        '''仅保Roi操作点'''
        # self.setEditMode(UICanvasCommonPathItem.BorderEditableMode, False)
        self.setEditMode(CanvasCommonPathItem.RoiEditableMode, False)
        self.setEditMode(CanvasCommonPathItem.HitTestMode, False)
        self.setEditMode(CanvasCommonPathItem.AdvanceSelectMode, False)

    def zoomHandle(self, zoomFactor):
        oldArrowStyleMap = self.styleAttribute.getValue().value()
        oldArrowStyleMap["brush"] = QBrush(QColor(255, 0, 0, int(100 * zoomFactor * 1.2)))
        self.styleAttribute.setValue(QVariant(oldArrowStyleMap))

    def customPaint(self, painter: QPainter, targetPath:QPainterPath) -> None:
        arrowStyleMap = self.styleAttribute.getValue().value()
        painter.setBrush(arrowStyleMap["brush"])
        painter.setPen(arrowStyleMap["pen"])
        painter.drawPath(targetPath)

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        self.zoomComponent.TriggerEvent(event.delta())

    def buildShapePath(self, targetPath:QPainterPath, targetPolygon:QPolygonF, isClosePath:bool):
        if self.shapeType == CanvasClosedShapeEnum.Ellipse:
            CanvasUtil.buildEllipsePath(targetPath, targetPolygon)
        elif self.shapeType == CanvasClosedShapeEnum.Rectangle:
            CanvasUtil.buildRectanglePath(targetPath, targetPolygon)
        elif self.shapeType == CanvasClosedShapeEnum.Star:
            CanvasUtil.buildStarPath(targetPath, targetPolygon)