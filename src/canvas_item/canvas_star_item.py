from .canvas_util import *

class CanvasStarItem(CanvasCommonPathItem):
    '''
    绘图工具-五角星图元
    '''
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.__initEditMode()
        self.__initStyle()

        self.zoomComponent = ZoomComponent()
        self.zoomComponent.signal.connect(self.zoomHandle)

    def __initStyle(self):
        self.defaultPenWidth = 3
        styleMap = {
            "brush" : QBrush(QColor(255, 0, 0, 255)),
            "pen" : QPen(QColor(255, 0, 0), self.defaultPenWidth, Qt.SolidLine),
        }
        self.styleAttribute = CanvasAttribute()
        self.styleAttribute.setValue(QVariant(styleMap))
        self.styleAttribute.valueChangedSignal.connect(self.update)

    def __initEditMode(self):
        '''仅保留边框操作点'''
        self.setEditMode(CanvasCommonPathItem.HitTestMode, False)
        self.setEditMode(CanvasCommonPathItem.RoiEditableMode, False)
        self.setEditMode(CanvasCommonPathItem.AdvanceSelectMode, False)

    def zoomHandle(self, zoomFactor):
        finalStyleMap = self.styleAttribute.getValue().value()

        finalBrush:QBrush = finalStyleMap["brush"]
        finalBrushColor = finalBrush.color()
        finalBrushColor.setAlpha(int(100 * zoomFactor * 1.2))
        finalBrush.setColor(finalBrushColor)
        finalStyleMap["brush"] = finalBrush

        finalPen:QPen = finalStyleMap["pen"]
        finalPenColor = finalPen.color()
        finalPenColor.setAlpha(int(100 * zoomFactor * 1.4))
        finalPen.setColor(finalPenColor)
        finalPenWidth = finalPen.width()
        finalPenWidth = int(self.defaultPenWidth * zoomFactor)
        finalPen.setWidth(finalPenWidth)
        finalStyleMap["pen"] = finalPen

        self.styleAttribute.setValue(QVariant(finalStyleMap))

    def customPaint(self, painter: QPainter, targetPath:QPainterPath) -> None:
        arrowStyleMap = self.styleAttribute.getValue().value()
        painter.setBrush(arrowStyleMap["brush"])
        painter.setPen(arrowStyleMap["pen"])
        painter.drawPath(targetPath)

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        self.zoomComponent.TriggerEvent(event.delta())

    def buildShapePath(self, targetPath:QPainterPath, targetPolygon:QPolygonF, isClosePath:bool):
        CanvasUtil.buildStarPath(targetPath, targetPolygon)