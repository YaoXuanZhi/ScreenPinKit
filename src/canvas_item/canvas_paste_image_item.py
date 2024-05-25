from PyQt5.QtWidgets import QGraphicsSceneMouseEvent
from .canvas_util import *

class CanvasPasteImageItem(CanvasCommonPathItem):
    '''
    绘图工具-图片粘贴图元
    '''
    def __init__(self, bgBrush:QBrush, parent: QWidget = None) -> None:
        super().__init__(parent, False)
        self.__initEditMode()
        self.bgBrush = bgBrush
        self.bgPixmap = self.bgBrush.texture()

    def __initEditMode(self):
        # self.setEditMode(CanvasCommonPathItem.BorderEditableMode, False)
        self.setEditMode(CanvasCommonPathItem.RoiEditableMode, False) 
        # self.setEditMode(CanvasCommonPathItem.AdvanceSelectMode, False) 
        # self.setEditMode(CanvasCommonPathItem.HitTestMode, False) # 如果想要显示当前HitTest区域，注释这行代码即可

    def type(self) -> int:
        return EnumCanvasItemType.CanvasEraserRectItem.value

    def hasFocusWrapper(self):
        return True

    def excludeControllers(self) -> list:
        return [EnumPosType.ControllerPosTT]

    def customPaint(self, painter: QPainter, targetPath:QPainterPath) -> None:
        # bug:目前实现方式在该图元旋转时会出现bug
        return self.customPaintByClip(painter, targetPath)
        # self.customPaintByCopy(painter, targetPath)

    def customPaintByCopy(self, painter: QPainter, targetPath:QPainterPath) -> None:
        painter.drawPixmap(self.boundingRect(), self.bgPixmap, self.sceneBoundingRect())

    def customPaintByClip(self, painter: QPainter, targetPath:QPainterPath) -> None:
        # 实现思路：假设该图元本来就能显示一个完整的背景，然后当前显示区是其裁剪所得的，类似头像裁剪框之类的思路

        # 裁剪出当前区域
        painter.setClipPath(targetPath)
        sourceRect = QRectF(QRect(QPoint(0, 0), self.bgPixmap.size()))
        targetRect = self.mapRectFromScene(sourceRect)

        # 始终将背景贴到整个view上
        # painter.drawPixmap(targetRect, self.bgPixmap, sourceRect)
        painter.drawPixmap(targetRect.topLeft().toPoint(), self.bgPixmap)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        return super().mouseMoveEvent(event)

    def getStretchableRect(self) -> QRect:
        return self.polygon.boundingRect()

    def buildShapePath(self, targetPath:QPainterPath, targetPolygon:QPolygonF, isClosePath:bool):
        CanvasUtil.buildRectanglePath(targetPath, targetPolygon)