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

    def excludeControllers(self) -> list:
        return [EnumPosType.ControllerPosTT]

    def customPaint(self, painter: QPainter, targetPath:QPainterPath) -> None:
        partRect = self.sceneBoundingRect().toRect()
        if partRect.width() < self.minSize.width() or partRect.height() < self.minSize.height():
            return

        # 性能损耗大，使用opencv实现版本在遇到较大区域的时候会出现程序闪退
        tempPixmap = self.sourcePixmap.copy(partRect)
        finalPixmap = AfterEffectUtilByPIL.gaussianBlur(tempPixmap, 5)
        # finalPixmap = AfterEffectUtilByPIL.mosaic(tempPixmap, 5, 1)
        painter.drawPixmap(self.boundingRect().topLeft(), finalPixmap)

        # painter.drawPixmap(self.boundingRect(), self.blurPixmap, self.sceneBoundingRect())

    def getStretchableRect(self) -> QRect:
        return self.polygon.boundingRect()

    def buildShapePath(self, targetPath:QPainterPath, targetPolygon:QPolygonF, isClosePath:bool):
        CanvasUtil.buildRectanglePath(targetPath, targetPolygon)