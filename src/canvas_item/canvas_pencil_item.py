from .canvas_util import *

class CanvasPencilItem(CanvasCommonPathItem):
    '''
    绘图工具-铅笔图元
    '''
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent, False)
        self.__initEditMode()
        self.__initStyle()

    def __initStyle(self):
        initPen = QPen(QColor(0, 255, 0, 100))
        initPen.setWidth(5)
        initPen.setCosmetic(True)
        initPen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        initPen.setCapStyle(Qt.PenCapStyle.RoundCap)
        arrowStyleMap = {
            "pen" : initPen,
        }
        self.styleAttribute = CanvasAttribute()
        self.styleAttribute.setValue(QVariant(arrowStyleMap))
        self.updatePen()
        self.styleAttribute.valueChangedSignal.connect(self.updatePen)

    def updatePen(self) -> None:
        oldArrowStyleMap = self.styleAttribute.getValue().value()
        finalPen:QPen = oldArrowStyleMap["pen"]
        self.m_penDefault = finalPen
        self.m_penSelected = finalPen
        self.update()

    def __initEditMode(self):
        self.setEditMode(CanvasCommonPathItem.BorderEditableMode, False)
        self.setEditMode(CanvasCommonPathItem.RoiEditableMode, False) 
        self.setEditMode(CanvasCommonPathItem.AdvanceSelectMode, False) 
        self.setEditMode(CanvasCommonPathItem.HitTestMode, False) # 如果想要显示当前HitTest区域，注释这行代码即可

    def wheelEvent(self, event: QGraphicsSceneWheelEvent) -> None:
        oldArrowStyleMap = self.styleAttribute.getValue().value()
        finalPen:QPen = oldArrowStyleMap["pen"]

        # 计算缩放比例
        if event.delta() > 0:
            newPenWidth = finalPen.width() + 1
        else:
            newPenWidth = max(1, finalPen.width() - 1)

        finalPen.setWidth(newPenWidth)

        styleMap = {
            "pen" : finalPen,
        }

        self.styleAttribute.setValue(QVariant(styleMap))

    def customPaint(self, painter: QPainter, targetPath:QPainterPath) -> None:
        styleMap = self.styleAttribute.getValue().value()
        painter.setPen(styleMap["pen"])
        painter.drawPath(targetPath)

    def buildShapePath(self, targetPath:QPainterPath, targetPolygon:QPolygonF, isClosePath:bool):
        targetPath.addPolygon(targetPolygon)

    def setEditableState(self, isEditable:bool):
        pass