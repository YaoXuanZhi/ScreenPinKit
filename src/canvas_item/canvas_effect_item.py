# coding=utf-8
from .canvas_util import *
from .after_effect_util import *

class CanvasEffectRectItem(CanvasCommonPathItem):
    '''
    绘图工具-特效图元
    '''
    def __init__(self, sourcePixmap:QPixmap, parent: QWidget = None) -> None:
        super().__init__(parent, False)
        self.sourcePixmap = sourcePixmap
        self.effectedPixmap = None
        self.effectWorker = EffectWorker()
        self.effectWorker.effectFinishedSignal.connect(self.onEffectFinished)
        self.minSize = QSize(5, 5)
        self.__initEditMode()
        self.__initStyle()

    def __initEditMode(self):
        # self.setEditMode(CanvasCommonPathItem.BorderEditableMode, False)
        self.setEditMode(CanvasCommonPathItem.RoiEditableMode, False) 
        self.setEditMode(CanvasCommonPathItem.AdvanceSelectMode, False) 
        self.setEditMode(CanvasCommonPathItem.HitTestMode, False) # 如果想要显示当前HitTest区域，注释这行代码即可

    def __initStyle(self):
        # 由于图元和工具栏是采用动态方式绑定的，必须确保绑定时触发一次valueChangedSignal
        styleMap = {
            "strength" : 5,
            "effectType" : AfterEffectType.Unknown,
        }
        self.styleAttribute = CanvasAttribute()
        self.styleAttribute.setValue(QVariant(styleMap))
        self.styleAttribute.valueChangedSignal.connect(self.styleAttributeChanged)

    def type(self) -> int:
        return EnumCanvasItemType.CanvasBlurItem.value

    def resetStyle(self, styleMap):
        self.styleAttribute.setValue(QVariant(styleMap))

    def styleAttributeChanged(self):
        styleMap = self.styleAttribute.getValue().value()
        strength = styleMap["strength"]
        effectType = styleMap["effectType"]
        self.effectWorker.startEffect(effectType, self.sourcePixmap, strength)

    def onEffectFinished(self, finalPixmap:QPixmap):
        self.effectedPixmap = finalPixmap
        self.effectedPixmap.setDevicePixelRatio(self.sourcePixmap.devicePixelRatio())
        self.update()

    def excludeControllers(self) -> list:
        return [EnumPosType.ControllerPosTT]

    def boundingRect(self) -> QRectF:
        self.attachPath.clear()

        # self.buildShapePath(self.attachPath, self.polygon, self.isClosePath)
        self.attachPath.addRoundedRect(self.polygon.boundingRect(), 6, 6)

        return self.attachPath.boundingRect()

    def customPaint(self, painter: QPainter, targetPath:QPainterPath) -> None:
        partRect = self.sceneBoundingRect().toRect()
        if partRect.width() < self.minSize.width() or partRect.height() < self.minSize.height():
            return

        self.customPaintByClip(painter, targetPath)
        # self.customPaintByCopy(painter, targetPath)
        return

        styleMap = self.styleAttribute.getValue().value()
        strength = styleMap["strength"]
        physicalPartRect = self.physicalRectF(partRect).toRect()
        partPixmap = self.sourcePixmap.copy(physicalPartRect)
        effectPixmap = AfterEffectUtilByPIL.gaussianBlur(partPixmap, strength)
        # effectPixmap = AfterEffectUtilByPIL.mosaic(partPixmap, 5, strength)
        sourceRect = QRectF(0, 0, partPixmap.width(), partPixmap.height())
        painter.drawPixmap(self.boundingRect(), effectPixmap, sourceRect)

    def physicalRectF(self, rectf:QRectF):
        pixelRatio = self.sourcePixmap.devicePixelRatio()
        return QRectF(rectf.x() * pixelRatio, rectf.y() * pixelRatio,
                      rectf.width() * pixelRatio, rectf.height() * pixelRatio)

    def customPaintByCopy(self, painter: QPainter, targetPath:QPainterPath) -> None:
        if self.effectedPixmap == None:
            return
        physicalRect = self.physicalRectF(self.sceneBoundingRect())
        painter.drawPixmap(self.boundingRect(), self.effectedPixmap, physicalRect)

    def customPaintByClip(self, painter: QPainter, targetPath:QPainterPath) -> None:
        if self.effectedPixmap == None:
            return
        # 实现思路：假设该图元本来就能显示一个完整的背景，然后当前显示区是其裁剪所得的，类似头像裁剪框之类的思路

        # 裁剪出当前区域
        painter.setClipPath(targetPath)
        topLeft = self.mapFromScene(QPoint(0, 0))

        # 始终将背景贴到整个view上
        painter.drawPixmap(topLeft, self.effectedPixmap)

    def getStretchableRect(self) -> QRect:
        return self.polygon.boundingRect()

    def buildShapePath(self, targetPath:QPainterPath, targetPolygon:QPolygonF, isClosePath:bool):
        CanvasUtil.buildRectanglePath(targetPath, targetPolygon)

    def applyShadow(self):
        shadowEffect = QGraphicsDropShadowEffect()
        shadowEffect.setBlurRadius(20)  # 阴影的模糊半径
        shadowEffect.setColor(QColor(0, 0, 0, 100))  # 阴影的颜色和透明度
        shadowEffect.setOffset(0, 0)  # 阴影的偏移量
        self.setGraphicsEffect(shadowEffect)