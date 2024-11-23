# coding=utf-8
from .canvas_util import *


class CanvasEraserItem(CanvasCommonPathItem):
    """
    绘图工具-橡皮擦
    """

    def __init__(
        self,
        pen: QPen = QPen(QColor(0, 255, 0, 100)),
        isSmoothCurve: bool = True,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent, False)
        self.__initEditMode()
        self.__initStyle(pen)
        self.isSmoothCurve = isSmoothCurve

    def __initStyle(self, pen: QPen):
        self.devicePixelRatio = CanvasUtil.getDevicePixelRatio()
        styleMap = {
            "width": 5,
        }
        self.usePen = pen
        self.usePen.setWidth(styleMap["width"] * self.devicePixelRatio)
        self.usePen.setCosmetic(True)
        self.usePen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        self.usePen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.styleAttribute = CanvasAttribute()
        self.styleAttribute.setValue(QVariant(styleMap))
        self.styleAttribute.valueChangedSignal.connect(self.styleAttributeChanged)

    def type(self) -> int:
        return EnumCanvasItemType.CanvasEraserItem.value

    def styleAttributeChanged(self):
        styleMap = self.styleAttribute.getValue().value()
        width = styleMap["width"]
        self.usePen.setWidth(width * self.devicePixelRatio)
        self.update()

    def resetStyle(self, styleMap):
        self.styleAttribute.setValue(QVariant(styleMap))

    def __initEditMode(self):
        self.setEditMode(CanvasCommonPathItem.BorderEditableMode, False)
        self.setEditMode(CanvasCommonPathItem.RoiEditableMode, False)
        self.setEditMode(CanvasCommonPathItem.AdvanceSelectMode, False)
        self.setEditMode(
            CanvasCommonPathItem.HitTestMode, False
        )  # 如果想要显示当前HitTest区域，注释这行代码即可
        self.setEditMode(CanvasCommonPathItem.ShadowEffectMode, False)

    def customPaint(self, painter: QPainter, targetPath: QPainterPath) -> None:
        painter.setPen(self.usePen)
        painter.drawPath(targetPath)

    def buildShapePath(
        self, targetPath: QPainterPath, targetPolygon: QPolygonF, isClosePath: bool
    ):
        if self.isSmoothCurve:
            CanvasUtil.polygon2BeizerPath(targetPath, targetPolygon)
        else:
            targetPath.addPolygon(targetPolygon)

    def setEditableState(self, isEditable: bool):
        """橡皮擦不允许绘制结束之后的重新编辑"""
        # return super().setEditableState(isEditable)
        pass


class CanvasEraserRectItem(CanvasCommonPathItem):
    """
    绘图工具-橡皮框图元
    """

    def __init__(self, bgBrush: QBrush, parent: QWidget = None) -> None:
        super().__init__(parent, False)
        self.__initEditMode()
        self.bgBrush = bgBrush
        self.bgPixmap = self.bgBrush.texture()

    def __initEditMode(self):
        # self.setEditMode(CanvasCommonPathItem.BorderEditableMode, False)
        self.setEditMode(CanvasCommonPathItem.RoiEditableMode, False)
        self.setEditMode(CanvasCommonPathItem.AdvanceSelectMode, False)
        self.setEditMode(
            CanvasCommonPathItem.HitTestMode, False
        )  # 如果想要显示当前HitTest区域，注释这行代码即可
        self.setEditMode(CanvasCommonPathItem.ShadowEffectMode, False)

    def type(self) -> int:
        return EnumCanvasItemType.CanvasEraserRectItem.value

    def excludeControllers(self) -> list:
        return [EnumPosType.ControllerPosTT]

    def customPaint(self, painter: QPainter, targetPath: QPainterPath) -> None:
        # bug:目前实现方式在该图元旋转时会出现bug
        # self.customPaintByClip(painter, targetPath)
        self.customPaintByCopy(painter, targetPath)

    def physicalRectF(self, rectf: QRectF):
        pixelRatio = self.bgPixmap.devicePixelRatio()
        return QRectF(
            rectf.x() * pixelRatio,
            rectf.y() * pixelRatio,
            rectf.width() * pixelRatio,
            rectf.height() * pixelRatio,
        )

    def customPaintByCopy(self, painter: QPainter, targetPath: QPainterPath) -> None:
        # 注意，这里面pixmap被复制的区域是经过放大后的区域，因此需要将屏幕区域做一次转换
        physicalRect = self.physicalRectF(self.sceneBoundingRect())
        painter.drawPixmap(self.boundingRect(), self.bgPixmap, physicalRect)

    def customPaintByClip(self, painter: QPainter, targetPath: QPainterPath) -> None:
        # 实现思路：假设该图元本来就能显示一个完整的背景，然后当前显示区是其裁剪所得的，类似头像裁剪框之类的思路

        # 裁剪出当前区域
        painter.setClipPath(targetPath)
        topLeft = self.mapFromScene(QPoint(0, 0))

        # 始终将背景贴到整个view上
        painter.drawPixmap(topLeft, self.bgPixmap)

    def getStretchableRect(self) -> QRect:
        return self.polygon.boundingRect()

    def buildShapePath(
        self, targetPath: QPainterPath, targetPolygon: QPolygonF, isClosePath: bool
    ):
        CanvasUtil.buildRectanglePath(targetPath, targetPolygon)


# class CanvasShadowEraserRectItem(CanvasEraserRectItem):
#     def initializedEvent(self):
#         self.applyShadow()

#     def applyShadow(self):
#         shadowEffect = QGraphicsDropShadowEffect()
#         shadowEffect.setBlurRadius(30)  # 阴影的模糊半径
#         shadowEffect.setColor(QColor(0, 0, 0, 150))  # 阴影的颜色和透明度
#         shadowEffect.setOffset(0, 0)  # 阴影的偏移量
#         self.setGraphicsEffect(shadowEffect)

#     def setEditableState(self, isEditable: bool):
#         pass

#     def type(self) -> int:
#         return EnumCanvasItemType.CanvasShadowEraserRectItem.value


class CanvasShadowEraserRectItem(QGraphicsRectItem):
    def __init__(self, bgBrush, parent=None):
        super().__init__(parent)
        self.devicePixelRatio = CanvasUtil.getDevicePixelRatio()
        self.bgBrush = bgBrush
        self.bgPixmap = self.bgBrush.texture()
        self.attachPath = QPainterPath()
        self.polygon = QPolygonF()
        self.applyShadow()

    def boundingRect(self) -> QRectF:
        self.attachPath.clear()
        self.attachPath.addRoundedRect(self.polygon.boundingRect(), 6, 6)
        return self.attachPath.boundingRect()

    def shape(self) -> QPainterPath:
        return self.attachPath

    def type(self) -> int:
        return EnumCanvasItemType.CanvasShadowEraserRectItem.value

    def customPaintByClip(self, painter: QPainter, targetPath: QPainterPath) -> None:
        # 实现思路：假设该图元本来就能显示一个完整的背景，然后当前显示区是其裁剪所得的，类似头像裁剪框之类的思路

        # 裁剪出当前区域
        painter.setClipPath(targetPath)
        topLeft = self.mapFromScene(QPoint(0, 0))

        # 始终将背景贴到整个view上
        painter.drawPixmap(topLeft, self.bgPixmap)

    def applyShadow(self):
        shadowEffect = QGraphicsDropShadowEffect()
        shadowEffect.setBlurRadius(30 * self.devicePixelRatio)  # 阴影的模糊半径
        shadowEffect.setColor(QColor(0, 0, 0, 150))  # 阴影的颜色和透明度
        shadowEffect.setOffset(0, 0)  # 阴影的偏移量
        self.setGraphicsEffect(shadowEffect)

    def paint(
        self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget
    ) -> None:
        self.customPaintByClip(painter, self.attachPath)

    def setEditableState(self, isEditable: bool):
        pass

    def completeDraw(self):
        pass
