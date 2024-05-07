from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import *
from icon import ScreenShotIcon
from .color_picker_button_plus import *
from .font_picker_button_plus import *
from canvas_editor import *
from canvas_item import *

class PolygonLineToolbar(CommandBarView):
    def __init__(self, canvasItem:QGraphicsItem = None, parent=None):
        super().__init__(parent=parent)
        self.canvasItem:CanvasPolygonItem = canvasItem
        self.initUI()

    def initUI(self):
        defaultAction = Action(ScreenShotIcon.STAR, '折线', triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawStar))
        self.addAction(defaultAction)
        self.addSeparator()

        # 线段选择
        lineDropdown = TransparentDropDownToolButton(ScreenShotIcon.POLYGONAL_LINE, self)
        lineDropdown.setIconSize(QSize(20, 20))
        lineDropdown.setMenu(self.createLineMenu(lineDropdown))
        self.addWidget(lineDropdown)

        self.addSeparator()

        # 边缘颜色选择
        self.penColorPickerButton = ColorPickerButtonPlus(Qt.GlobalColor.yellow, 'Edge Background Color', self, enableAlpha=True)
        self.penColorPickerButton.setToolTip("边缘颜色")
        self.penColorPickerButton.setFixedSize(30, 30)
        self.addWidget(self.penColorPickerButton)

        # 内容颜色选择
        self.brushColorPickerButton = ColorPickerButtonPlus(Qt.GlobalColor.yellow, 'Content Background Color', self, enableAlpha=True)
        self.brushColorPickerButton.setToolTip("填充颜色")
        self.brushColorPickerButton.setFixedSize(30, 30)
        self.addWidget(self.brushColorPickerButton)

    def createLineMenu(self, button:PrimarySplitPushButton):
        menu = RoundMenu(parent=self)
        menu.setFixedWidth(20)
        menu.addActions([
            Action(ScreenShotIcon.POLYGONAL_LINE, "虚线", triggered=lambda c, b=button: self.onMenuClicked(c, b, ScreenShotIcon.POLYGONAL_LINE)),
            Action(ScreenShotIcon.ARROW, "实线", triggered=lambda c, b=button: self.onMenuClicked(c, b, ScreenShotIcon.ARROW)),
        ])
        return menu

    def onMenuClicked(self, c, button:PrimarySplitPushButton, icon):
        button.setIcon(icon)

    def showEvent(self, a0: QShowEvent) -> None:
        self.hBoxLayout.setContentsMargins(1, 1, 1, 1)
        self.setIconSize(QSize(20, 20))
        self.resizeToSuitableWidth()
        self.adjustSize()
        return super().showEvent(a0)

    def switchDrawTool(self, drawActionEnum:DrawActionEnum, cursor:QCursor = Qt.CursorShape.CrossCursor):
        print(f"=======> {drawActionEnum}")