from .canvas_util import *

class CanvasEraserItem(CanvasCommonPathItem):
    '''
    绘图工具-橡皮擦图元
    '''
    def __init__(self, pen:QPen = QPen(QColor(0, 255, 0, 100)), isSmoothCurve:bool = True, parent: QWidget = None) -> None:
        super().__init__(parent, False)
        self.__initEditMode()
        self.__initStyle(pen)
        self.isSmoothCurve = isSmoothCurve

    def __initStyle(self, pen:QPen):
        initPen = pen
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

    def type(self) -> int:
        return EnumCanvasItemType.CanvasEraserItem.value

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
        oldStyleMap = self.styleAttribute.getValue().value()
        finalPen:QPen = oldStyleMap["pen"]

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
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.setPen(styleMap["pen"])
        painter.drawPath(targetPath)

    def buildShapePath(self, targetPath:QPainterPath, targetPolygon:QPolygonF, isClosePath:bool):
        if self.isSmoothCurve:
            CanvasUtil.polygon2BeizerPath(targetPath, targetPolygon)
        else:
            targetPath.addPolygon(targetPolygon)

    def setEditableState(self, isEditable: bool):
        '''橡皮擦不允许绘制结束之后的重新编辑'''
        # return super().setEditableState(isEditable)
        pass

class CanvasEraserRectItem(CanvasCommonPathItem):
    '''
    绘图工具-橡皮擦矩形图元
    '''
    def __init__(self, bgBrush:QBrush, parent: QWidget = None) -> None:
        super().__init__(parent, False)
        self.__initEditMode()
        self.bgBrush = bgBrush
        self.bgPixmap = self.bgBrush.texture()

    def __initEditMode(self):
        self.setEditMode(CanvasCommonPathItem.BorderEditableMode, False)
        self.setEditMode(CanvasCommonPathItem.RoiEditableMode, False) 
        self.setEditMode(CanvasCommonPathItem.AdvanceSelectMode, False) 
        self.setEditMode(CanvasCommonPathItem.HitTestMode, False) # 如果想要显示当前HitTest区域，注释这行代码即可

    def type(self) -> int:
        return EnumCanvasItemType.CanvasEraserRectItem.value

    def excludeControllers(self) -> list:
        return [EnumPosType.ControllerPosTT]

    def customPaint(self, painter: QPainter, targetPath:QPainterPath) -> None:
        # bug:目前实现方式在该图元旋转时会出现bug
        # return self.customPaintByClip(painter, targetPath)
        self.customPaintByCopy(painter, targetPath)

    def customPaintByCopy(self, painter: QPainter, targetPath:QPainterPath) -> None:
        painter.drawPixmap(self.boundingRect(), self.bgPixmap, self.sceneBoundingRect())

    def customPaintByClip(self, painter: QPainter, targetPath:QPainterPath) -> None:
        # 实现思路：假设该图元本来就能显示一个完整的背景，然后当前显示区是其裁剪所得的，类似头像裁剪框之类的思路

        # 裁剪出当前区域
        painter.setClipPath(targetPath)
        sourceRect = QRectF(QRect(QPoint(0, 0), self.bgPixmap.size()))
        targetRect = self.mapRectFromScene(sourceRect)

        # 始终将背景贴到整个view上
        painter.drawPixmap(targetRect, self.bgPixmap, sourceRect)

    def getStretchableRect(self) -> QRect:
        return self.polygon.boundingRect()

    def buildShapePath(self, targetPath:QPainterPath, targetPolygon:QPolygonF, isClosePath:bool):
        CanvasUtil.buildRectanglePath(targetPath, targetPolygon)