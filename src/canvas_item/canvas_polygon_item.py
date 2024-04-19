import sys, math
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from .canvas_util import *

class CanvasPolygonItem(CanvasCommonPathItem):
    '''
    绘图工具-折线图元

    Note:
    对于一个非封闭的PathItem而言，为了让它的HitTest行为约束在线段内，将其
    shape()里的shapePath由相邻两点加上线条宽度构成的连续矩形合并；
    另一方面，最终显示出来的线条则是QPen直接绘制原始PathItem所得
    '''
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent, False)
        self.__initEditMode()
        self.__initStyle()
        self.paintPath = QPainterPath()

    def __initStyle(self):
        initPen = QPen(QColor(255, 255, 0, 100))
        initPen.setWidth(32)
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

    def getOffsetLength(self) -> int:
        '''
        Note:
        由于抗锯齿等渲染技术的影响，实际渲染的宽度可能会比设置的宽度略大，
        需要拿到QPaint.device().devicePixelRatioF()来进行转换处理
        '''
        oldArrowStyleMap = self.styleAttribute.getValue().value()
        finalPen:QPen = oldArrowStyleMap["pen"]
        finalLength = int(finalPen.width() / 2) / self.devicePixelRatio
        return finalLength 

    def __initEditMode(self):
        '''仅保Roi操作点'''
        self.setEditMode(CanvasCommonPathItem.BorderEditableMode, False)
        # self.setEditMode(UICanvasCommonPathItem.AdvanceSelectMode, False) 
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

        arrowStyleMap = {
            "pen" : finalPen,
        }

        self.styleAttribute.setValue(QVariant(arrowStyleMap))

    def customPaint(self, painter: QPainter, targetPath:QPainterPath) -> None:
        styleMap = self.styleAttribute.getValue().value()
        painter.setPen(styleMap["pen"])
        painter.drawPath(self.paintPath)

        if self.isHitTestMode():
            painter.setPen(QPen(Qt.red, 1, Qt.DashLine))
            painter.drawPath(targetPath)

    def buildShapePath(self, targetPath:QPainterPath, targetPolygon:QPolygonF, isClosePath:bool):
        self.paintPath.clear()
        CanvasUtil.buildSegmentsPath(self.paintPath, targetPolygon, isClosePath)
        super().buildShapePath(targetPath, targetPolygon, isClosePath)