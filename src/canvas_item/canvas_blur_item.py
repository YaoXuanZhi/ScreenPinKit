# 参考acrylic_label.py控件的实现
from typing import Any
from PyQt5.QtGui import QPaintEvent
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsSceneMouseEvent
from .canvas_util import *
from .blur_util import *

class CanvasBlurRectItem(CanvasCommonPathItem):
    '''
    绘图工具-模糊矩形图元
    '''
    def __init__(self, sourcePixmap:QPixmap, blurPixmap:QPixmap, parent: QWidget = None) -> None:
        super().__init__(parent, False)
        self.sourcePixmap = sourcePixmap
        self.blurPixmap = blurPixmap
        self.__initEditMode()

    def __initEditMode(self):
        # self.setEditMode(CanvasCommonPathItem.BorderEditableMode, False)
        self.setEditMode(CanvasCommonPathItem.RoiEditableMode, False) 
        self.setEditMode(CanvasCommonPathItem.AdvanceSelectMode, False) 
        self.setEditMode(CanvasCommonPathItem.HitTestMode, False) # 如果想要显示当前HitTest区域，注释这行代码即可

    def excludeControllers(self) -> list:
        return [EnumPosType.ControllerPosTT]

    def customPaint(self, painter: QPainter, targetPath:QPainterPath) -> None:
        if self.polygon.at(0) == self.polygon.at(1):
            return

        # ctrl+t生成的FreezeWindow会出现显示白线，背景显示不正常
        # 性能损耗大
        # tempPixmap = self.sourcePixmap.copy(self.sceneBoundingRect().toRect())
        # finalPixmap = BlurUtil.gaussianBlur(tempPixmap, blurRadius=10)
        # painter.drawPixmap(self.boundingRect().topLeft(), finalPixmap)

        painter.drawPixmap(self.boundingRect(), self.blurPixmap, self.sceneBoundingRect())

        # painter.drawPixmap(self.boundingRect(), self.sourcePixmap, self.sceneBoundingRect())

    def getStretchableRect(self) -> QRect:
        return self.polygon.boundingRect()

    def buildShapePath(self, targetPath:QPainterPath, targetPolygon:QPolygonF, isClosePath:bool):
        CanvasUtil.buildRectanglePath(targetPath, targetPolygon)

    # def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
    #     if event.button() == Qt.MouseButton.RightButton:
    #         tempPixmap = self.sourcePixmap.copy(self.sceneBoundingRect().toRect())
    #         finalPixmap = BlurUtil.gaussianBlur(tempPixmap, blurRadius=2)
    #         path = f"blurPixmap-{tempPixmap.size().width()}-{finalPixmap.size().height()}.png"
    #         finalPixmap.save(path)

    #     return super().mouseDoubleClickEvent(event)