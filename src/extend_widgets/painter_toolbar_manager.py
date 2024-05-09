from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import *
from icon import ScreenShotIcon
from .color_picker_button_plus import *
from .font_picker_button_plus import *
from canvas_editor import *
from canvas_item import *
from .shape_toolbar import *
from .text_edit_toolbar import *
from .bubble_tip import *

class PainterToolBarManager:
    def __init__(self, targetWidget:QWidget) -> None:
        self.currentDrawActionEnum = DrawActionEnum.DrawNone
        self.targetWidget = targetWidget
        self.canvasItemBar:CommandBarView = None
        self.optionBar:QWidget = None
        self.toolBarMap = {
            type(ShapeToolbar) : [DrawActionEnum.DrawRectangle, DrawActionEnum.DrawEllipse],
            type(TextEditToolbar) : [DrawActionEnum.EditText],
        }

    def closeToolBar(self):
        if self.optionBar == None:
            return
        self.optionBar.close()
        self.optionBar.destroy()
        self.optionBar = None
        self.canvasItemBar = None

    def switchSelectItemToolBar(self, canvasItem:QGraphicsItem, sceneUserNotifyEnum:SceneUserNotifyEnum):
        '''
        切换选中的图元

        1. 如果类型相同，则直接进行重新绑定
        2. 如果类型不同，则更换工具栏
        '''
        if canvasItem == None:
            return

        drawActionEnum = DrawActionEnum.DrawNone
        if isinstance(self.canvasItemBar, TextEditToolbar):
            drawActionEnum = DrawActionEnum.EditText
        elif isinstance(self.canvasItemBar, ShapeToolbar):
            drawActionEnum = DrawActionEnum.DrawRectangle

        matchDrawActionEnum = DrawActionEnum.DrawNone
        if isinstance(canvasItem, CanvasTextItem):
            matchDrawActionEnum = DrawActionEnum.EditText
        elif isinstance(canvasItem, CanvasClosedShapeItem):
            matchDrawActionEnum = DrawActionEnum.DrawRectangle

        if drawActionEnum != matchDrawActionEnum:
            self.switchDrawTool(matchDrawActionEnum)

        if hasattr(self.canvasItemBar, "bindCanvasItem"):
            self.canvasItemBar.bindCanvasItem(canvasItem, sceneUserNotifyEnum)

    def switchDrawTool(self, drawActionEnum:DrawActionEnum) -> CommandBarView:
        if self.currentDrawActionEnum == drawActionEnum:
            return

        if self.currentDrawActionEnum != DrawActionEnum.DrawNone and self.currentDrawActionEnum != drawActionEnum:
            self.closeToolBar()

        self.currentDrawActionEnum = drawActionEnum
        if drawActionEnum == DrawActionEnum.SelectItem:
            self.closeToolBar()
            return

        if self.canvasItemBar == None:
            if drawActionEnum == DrawActionEnum.EditText:
                self.canvasItemBar = TextEditToolbar(parent=self.targetWidget)
            elif drawActionEnum == DrawActionEnum.DrawRectangle:
                self.canvasItemBar = ShapeToolbar(parent=self.targetWidget)

        self.optionBar = BubbleTip.make(
            target=self.targetWidget,
            view=self.canvasItemBar,
            duration=-1,
            tailPosition=BubbleTipTailPosition.TOP_LEFT,
            orientLength=4,
            parent=self.targetWidget,
            )