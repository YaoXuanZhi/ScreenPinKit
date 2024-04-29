from .canvas_util import *

class CanvasArrowItem(CanvasCommonPathItem):
    '''
    绘图工具-箭头图元
    '''
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.__initEditMode()
        self.__initStyle()

        self.zoomComponent = ZoomComponent()
        self.zoomComponent.zoomClamp = True
        self.zoomComponent.signal.connect(self.zoomHandle)

    def __initStyle(self):
        arrowStyleMap = {
            "arrowLength" : 32.0,
            "arrowAngle" : 0.5,
            "arrowBodyLength" : 18,
            "arrowBodyAngle" : 0.2,

            "arrowBrush" : QBrush(QColor(255, 0, 0, 100)),
            "arrowPen" : QPen(QColor(255, 0, 0), 2, Qt.SolidLine),
        }
        self.styleAttribute = CanvasAttribute()
        self.styleAttribute.setValue(QVariant(arrowStyleMap))
        self.styleAttribute.valueChangedSignal.connect(self.update)

    def __initEditMode(self):
        '''仅保Roi操作点'''
        self.setEditMode(CanvasCommonPathItem.BorderEditableMode, False)
        self.setEditMode(CanvasCommonPathItem.HitTestMode, False)
        self.setEditMode(CanvasCommonPathItem.AdvanceSelectMode, False)

    def zoomHandle(self, zoomFactor):
        oldArrowStyleMap = self.styleAttribute.getValue().value()
        oldArrowStyleMap["arrowLength"] = oldArrowStyleMap["arrowLength"] * zoomFactor
        oldArrowStyleMap["arrowBodyLength"] = oldArrowStyleMap["arrowBodyLength"] * zoomFactor
        oldArrowStyleMap["arrowBrush"] = QBrush(QColor(255, 0, 0, int(100 * zoomFactor * 1.2)))
        self.styleAttribute.setValue(QVariant(oldArrowStyleMap))

    def customPaint(self, painter: QPainter, targetPath:QPainterPath) -> None:
        arrowStyleMap = self.styleAttribute.getValue().value()
        painter.setBrush(arrowStyleMap["arrowBrush"])
        painter.setPen(arrowStyleMap["arrowPen"])
        painter.drawPath(targetPath)

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        self.zoomComponent.TriggerEvent(event.delta())

    def buildShapePath(self, targetPath:QPainterPath, targetPolygon:QPolygonF, isClosePath:bool):
        arrowStyleMap = self.styleAttribute.getValue().value()
        CanvasUtil.buildArrowPath(targetPath, targetPolygon, arrowStyleMap)