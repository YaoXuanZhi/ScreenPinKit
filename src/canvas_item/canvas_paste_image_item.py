# coding=utf-8
from .canvas_util import *

class CanvasPasteImageItem(CanvasCommonPathItem):
    '''
    绘图工具-图片粘贴图元
    '''
    def __init__(self, bgBrush:QBrush, parent: QWidget = None) -> None:
        super().__init__(parent, False)
        self.__initEditMode()
        self.radius = 5
        self.bgBrush = bgBrush
        self.bgPixmap = self.bgBrush.texture()
        finalPixmap, finalGeometry = CanvasUtil.grabScreens()
        self.limitRect = finalGeometry

        self.edgeColor = QColor(30, 120, 255, 255)
        self.usePen = QPen(self.edgeColor, 2, Qt.PenStyle.SolidLine)
        self.useBrush = QBrush(self.edgeColor)

    def getEdgeOffset(self) -> int:
        return 0

    def __initEditMode(self):
        # self.setEditMode(CanvasCommonPathItem.BorderEditableMode, False)
        self.setEditMode(CanvasCommonPathItem.RoiEditableMode, False) 
        # self.setEditMode(CanvasCommonPathItem.AdvanceSelectMode, False) 
        self.setEditMode(CanvasCommonPathItem.HitTestMode, False) # 如果想要显示当前HitTest区域，注释这行代码即可

    def hasFocusWrapper(self):
        return True

    def excludeControllers(self) -> list:
        return [EnumPosType.ControllerPosTT]

    def customPaint(self, painter: QPainter, targetPath:QPainterPath) -> None:
        # bug:目前实现方式在该图元旋转时会出现bug
        return self.customPaintByClip(painter, targetPath)
        # self.customPaintByCopy(painter, targetPath)

    def physicalRectF(self, rectf:QRectF):
        pixelRatio = self.bgPixmap.devicePixelRatio()
        return QRectF(rectf.x() * pixelRatio, rectf.y() * pixelRatio,
                      rectf.width() * pixelRatio, rectf.height() * pixelRatio)
    def customPaintByCopy(self, painter: QPainter, targetPath:QPainterPath) -> None:
        # 注意，这里面pixmap被复制的区域是经过放大后的区域，因此需要将屏幕区域做一次转换
        physicalRect = self.physicalRectF(self.sceneBoundingRect())
        painter.drawPixmap(self.boundingRect(), self.bgPixmap, physicalRect)

    def customPaintByClip(self, painter: QPainter, targetPath:QPainterPath) -> None:
        # 实现思路：假设该图元本来就能显示一个完整的背景，然后当前显示区是其裁剪所得的，类似头像裁剪框之类的思路

        # 裁剪出当前区域
        painter.setClipPath(targetPath)
        topLeft = self.mapFromScene(QPoint(0, 0))

        # 始终将背景贴到整个view上
        painter.drawPixmap(topLeft, self.bgPixmap)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        return super().mouseMoveEvent(event)

    def getStretchableRect(self) -> QRect:
        return self.polygon.boundingRect()

    def buildShapePath(self, targetPath:QPainterPath, targetPolygon:QPolygonF, isClosePath:bool):
        CanvasUtil.buildRectanglePath(targetPath, targetPolygon)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        self.devicePixelRatio = painter.device().devicePixelRatioF()
        painter.save()
        self.customPaint(painter, self.attachPath)
        painter.restore()

        painter.save()
        painter.setPen(self.usePen)
        rect = self.getStretchableRect()
        painter.drawRect(rect)
        painter.restore()

        # 更新边框操作点位置
        if self.isBorderEditableMode():
            if self.hasFocusWrapper():
                self.initControllers()
            else:
                self.hideControllers()

    def initControllers(self):
        super().initControllers()

        if hasattr(self, "controllers"):
            pen = QPen()
            pen.setColor(Qt.GlobalColor.white)
            pen.setWidth(1)
            brush = QBrush(self.useBrush)
            for item in self.controllers:
                item.setPen(pen)
                item.setBrush(brush)