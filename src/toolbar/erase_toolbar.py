# coding=utf-8
from common import ScreenShotIcon, cfg
from canvas_editor import DrawActionEnum
from .canvas_item_toolbar import *


class EraseToolbar(CanvasItemToolBar):
    eraseTypeChangedSignal = pyqtSignal(DrawActionEnum)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def initDefaultStyle(self):
        self.styleMap = {
            "width": cfg.get(cfg.eraseToolbarWidth),
        }

    def initUI(self):
        self.addSeparator()
        eraseActions = [
            Action(
                ScreenShotIcon.FULL_Dot,
                self.tr("Eraser pen"),
                triggered=lambda: self.eraseTypeChangedSignal.emit(
                    DrawActionEnum.UseEraser
                ),
            ),
            Action(
                ScreenShotIcon.FULL_RECTANGLE,
                self.tr("Eraser frame"),
                triggered=lambda: self.eraseTypeChangedSignal.emit(
                    DrawActionEnum.UseEraserRectItem
                ),
            ),
            Action(
                ScreenShotIcon.SHADOW_ERASER,
                self.tr("Shadow Eraser frame"),
                triggered=lambda: self.eraseTypeChangedSignal.emit(
                    DrawActionEnum.UseShadowEraserRectItem
                ),
            ),
            Action(
                ScreenShotIcon.SHADOW_ELLIPSE_ERASER,
                self.tr("Shadow Eraser ellipse"),
                triggered=lambda: self.eraseTypeChangedSignal.emit(
                    DrawActionEnum.UseShadowEraserEllipseItem
                ),
            ),
        ]

        self.actionGroup = QActionGroup(self)
        for action in eraseActions:
            action.setCheckable(True)
            self.actionGroup.addAction(action)

        self.addActions(eraseActions)

        eraseActions[0].trigger()
        self.addSeparator()

    def refreshStyleUI(self):
        pass

    def refreshAttachItem(self):
        if self.canvasItem != None and hasattr(self.canvasItem, "resetStyle"):
            self.canvasItem.resetStyle(self.styleMap.copy())

    def wheelZoom(self, angleDelta: int, kwargs):
        finalValue = self.styleMap["width"]
        (minValue, maxValue) = cfg.eraseToolbarWidth.range

        if angleDelta > 1:
            finalValue = min(maxValue, finalValue + 2)
        else:
            finalValue = max(minValue, finalValue - 2)
        self.styleMap["width"] = finalValue
