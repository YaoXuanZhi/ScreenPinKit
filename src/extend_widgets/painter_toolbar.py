from PyQt5.QtGui import QShowEvent
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import *
from icon import ScreenShotIcon
from .color_picker_button_plus import *
from .font_picker_button_plus import *
from canvas_editor import CanvasEditor, DrawActionEnum

class TextEditToolbar(CommandBarView):
    def __init__(self, title: str, content: str, icon: QIcon = None,
                image: QImage = None, isClosable=False, parent=None):
        super().__init__(parent=parent)
        self.initUI()

    def initUI(self):
        fillModeActions = [
            Action(ScreenShotIcon.ARROW, '加粗', triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawArrow)),
            Action(ScreenShotIcon.STAR, '斜体', triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawStar)),
            Action(ScreenShotIcon.STAR, '阴影', triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawStar)),
        ]
        for action in fillModeActions:
            self.addAction(action)
        self.addSeparator()

        # 字体选择
        self.fontPickerButton = FontPickerButtonPlus(self.font(), '字体风格', self)
        self.fontPickerButton.setToolTip("字体选择")
        self.addWidget(self.fontPickerButton)

        # 文本颜色选择
        self.textColorPickerButton = ColorPickerButtonPlus(Qt.GlobalColor.yellow, 'Text Color', self, enableAlpha=True)
        self.textColorPickerButton.setToolTip("文本颜色")
        self.textColorPickerButton.setFixedSize(30, 30)
        self.addWidget(self.textColorPickerButton)

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

class PolygonLineToolbar(CommandBarView):
    def __init__(self, title: str, content: str, icon: QIcon = None,
                image: QImage = None, isClosable=False, parent=None):
        super().__init__(parent=parent)
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

class PenToolbar(CommandBarView):
    def __init__(self, title: str, content: str, icon: QIcon = None,
                image: QImage = None, isClosable=False, parent=None):
        super().__init__(parent=parent)
        self.initUI()

    def initUI(self):
        defaultAction = Action(ScreenShotIcon.STAR, '五角星', triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawStar))
        self.addAction(defaultAction)
        self.addSeparator()

        # 铅笔选择
        penDropdown = TransparentDropDownToolButton(ScreenShotIcon.POLYGONAL_LINE, self)
        penDropdown.setIconSize(QSize(20, 20))
        penDropdown.setMenu(self.createPenMenu(penDropdown))
        self.addWidget(penDropdown)

        self.addSeparator()

        # 颜色选择
        self.colorPickerButton = ColorPickerButtonPlus(Qt.GlobalColor.yellow, 'Background Color', self, enableAlpha=True)
        self.colorPickerButton.setFixedSize(30, 30)
        self.addWidget(self.colorPickerButton)

    def createPenMenu(self, button:PrimarySplitPushButton):
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

class ShapeToolbar(CommandBarView):
    def __init__(self, title: str, content: str, icon: QIcon = None,
                image: QImage = None, isClosable=False, parent=None):
        super().__init__(parent=parent)
        self.initUI()

    def initUI(self):
        fillModeActions = [
            Action(ScreenShotIcon.ARROW, '点', triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawArrow)),
            Action(ScreenShotIcon.STAR, '面', triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawStar)),
        ]

        self.actionGroup = QActionGroup(self)
        for action in fillModeActions:
            action.setCheckable(True)
            self.actionGroup.addAction(action)

        self.addActions(fillModeActions)
        self.addSeparator()

        # 多边形选择
        shapeDropdown = TransparentDropDownToolButton(ScreenShotIcon.RECTANGLE, self)
        shapeDropdown.setIconSize(QSize(20, 20))
        # shapeDropdown.setFlyout(self.createShapeMenu(shapeDropdown))
        shapeDropdown.setMenu(self.createShapeMenu(shapeDropdown))
        self.addWidget(shapeDropdown)

        self.addSeparator()

        # 颜色选择
        self.colorPickerButton = ColorPickerButtonPlus(Qt.GlobalColor.yellow, 'Background Color', self, enableAlpha=True)
        self.colorPickerButton.setFixedSize(30, 30)
        self.addWidget(self.colorPickerButton)

    def createShapeMenu(self, button:PrimarySplitPushButton):
        menu = RoundMenu(parent=self)
        menu.setFixedWidth(20)
        menu.addActions([
            Action(ScreenShotIcon.RECTANGLE, "矩形", triggered=lambda c, b=button: self.onMenuClicked(c, b, ScreenShotIcon.RECTANGLE)),
            Action(ScreenShotIcon.BRUSH, "圆形", triggered=lambda c, b=button: self.onMenuClicked(c, b, ScreenShotIcon.BRUSH)),
            Action(ScreenShotIcon.STAR, "五角星", triggered=lambda c, b=button: self.onMenuClicked(c, b, ScreenShotIcon.STAR)),
            Action(ScreenShotIcon.ARROW, "箭头", triggered=lambda c, b=button: self.onMenuClicked(c, b, ScreenShotIcon.ARROW)),
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