from .canvas_util import *
from .after_effect_util import *

class CanvasBlurRectItem(CanvasCommonPathItem):
    '''
    绘图工具-模糊矩形图元
    '''
    def __init__(self, sourcePixmap:QPixmap, parent: QWidget = None) -> None:
        super().__init__(parent, False)
        self.sourcePixmap = sourcePixmap
        self.blurPixmap = None
        self.effectWorker = EffectWorker(AfterEffectType.GaussianBlur)
        # self.effectWorker = EffectWorker(AfterEffectType.Mosaic)
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
        styleMap = {
            "strength" : 1,
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
        self.effectWorker.startEffect(self.sourcePixmap, strength)

    def onEffectFinished(self, finalPixmap:QPixmap):
        self.blurPixmap = finalPixmap
        self.update()

    def excludeControllers(self) -> list:
        return [EnumPosType.ControllerPosTT]

    def customPaint(self, painter: QPainter, targetPath:QPainterPath) -> None:
        partRect = self.sceneBoundingRect().toRect()
        if partRect.width() < self.minSize.width() or partRect.height() < self.minSize.height():
            return

        self.customPaintByCopy(painter, targetPath)
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
        if self.blurPixmap == None:
            return
        physicalRect = self.physicalRectF(self.sceneBoundingRect())
        painter.drawPixmap(self.boundingRect(), self.blurPixmap, physicalRect)

    def getStretchableRect(self) -> QRect:
        return self.polygon.boundingRect()

    def buildShapePath(self, targetPath:QPainterPath, targetPolygon:QPolygonF, isClosePath:bool):
        CanvasUtil.buildRectanglePath(targetPath, targetPolygon)