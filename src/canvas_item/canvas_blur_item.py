# 参考acrylic_label.py控件的实现
from typing import Any
from PyQt5.QtGui import QPaintEvent
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsSceneMouseEvent
from .canvas_util import *
from .after_effect_util import *
class CanvasBlurRectItem(CanvasCommonPathItem):
    '''
    绘图工具-模糊矩形图元
    '''
    def __init__(self, sourcePixmap:QPixmap, blurPixmap:QPixmap, parent: QWidget = None) -> None:
        super().__init__(parent, False)
        self.sourcePixmap = sourcePixmap
        self.blurPixmap = blurPixmap
        self.minSize = QSize(5, 5)
        self.__initEditMode()

    def __initEditMode(self):
        # self.setEditMode(CanvasCommonPathItem.BorderEditableMode, False)
        self.setEditMode(CanvasCommonPathItem.RoiEditableMode, False) 
        self.setEditMode(CanvasCommonPathItem.AdvanceSelectMode, False) 
        self.setEditMode(CanvasCommonPathItem.HitTestMode, False) # 如果想要显示当前HitTest区域，注释这行代码即可

    def type(self) -> int:
        return EnumCanvasItemType.CanvasBlurItem.value

    def excludeControllers(self) -> list:
        return [EnumPosType.ControllerPosTT]

    def customPaint(self, painter: QPainter, targetPath:QPainterPath) -> None:
        partRect = self.sceneBoundingRect().toRect()
        if partRect.width() < self.minSize.width() or partRect.height() < self.minSize.height():
            return

        # 计算两个矩形的重合区域

        # self.customPaintByClip(painter, targetPath)
        # self.customPaintByCopy(painter, targetPath)
        # return

        # 性能损耗大，使用opencv实现版本在遇到较大区域的时候会出现程序闪退
        physicalPartRect = self.physicalRectF(partRect).toRect()
        partPixmap = self.sourcePixmap.copy(physicalPartRect)
        effectPixmap = AfterEffectUtilByPIL.gaussianBlur(partPixmap, 2)
        # effectPixmap = AfterEffectUtilByPIL.mosaic(partPixmap, 5, 1)
        sourceRect = QRectF(0, 0, partPixmap.width(), partPixmap.height())
        painter.drawPixmap(self.boundingRect(), effectPixmap, sourceRect)

    def physicalRectF(self, rectf:QRectF):
        pixelRatio = self.sourcePixmap.devicePixelRatio()
        return QRectF(rectf.x() * pixelRatio, rectf.y() * pixelRatio,
                      rectf.width() * pixelRatio, rectf.height() * pixelRatio)

    def customPaintByCopy(self, painter: QPainter, targetPath:QPainterPath) -> None:
        physicalRect = self.physicalRectF(self.sceneBoundingRect())
        painter.drawPixmap(self.boundingRect(), self.blurPixmap, physicalRect)

    def customPaintByClip(self, painter: QPainter, targetPath:QPainterPath) -> None:
        # 实现思路：假设该图元本来就能显示一个完整的背景，然后当前显示区是其裁剪所得的，类似头像裁剪框之类的思路

        # 裁剪出当前区域
        painter.setClipPath(targetPath)
        sourceRect = QRectF(QRect(QPoint(0, 0), self.blurPixmap.size()))
        targetRect = self.mapRectFromScene(sourceRect)

        # 始终将背景贴到整个view上
        painter.drawPixmap(targetRect, self.blurPixmap, sourceRect)

    def getStretchableRect(self) -> QRect:
        return self.polygon.boundingRect()

    def buildShapePath(self, targetPath:QPainterPath, targetPolygon:QPolygonF, isClosePath:bool):
        CanvasUtil.buildRectanglePath(targetPath, targetPolygon)