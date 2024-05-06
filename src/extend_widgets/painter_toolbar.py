from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import *
from icon import ScreenShotIcon
from .color_picker_button_plus import *
from .font_picker_button_plus import *
from canvas_editor import *
from canvas_item import *

class TextEditToolbar(CommandBarView):
    def __init__(self, canvasItem:QGraphicsItem = None, parent=None):
        super().__init__(parent=parent)
        self.canvasItem:CanvasTextItem = canvasItem
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

class PenToolbar(CommandBarView):
    def __init__(self, canvasItem:QGraphicsItem = None, parent=None):
        super().__init__(parent=parent)
        self.canvasItem:CanvasPencilItem = canvasItem
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
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.initDefaultStyle()
        self.initUI()
        self.refreshStyleUI()
        self.listenerEvent()
        self.canvasItem = None

    def initDefaultStyle(self):
        self.opacity:int = 100
        self.styleMap = {
            "brush" : QBrush(QColor(255, 0, 0, 100)),
            "pen" : QPen(QColor(255, 0, 0), 2, Qt.PenStyle.SolidLine),
            "shape" : CanvasClosedShapeEnum.Rectangle,
        }

        self.outlineTypeInfos = [
            ("实线", Qt.PenStyle.SolidLine),
            ("虚线", Qt.PenStyle.DashLine),
        ]

        self.shapeTypeInfos = [
            ("矩形", ScreenShotIcon.RECTANGLE, CanvasClosedShapeEnum.Rectangle),
            ("圆形", ScreenShotIcon.CIRCLE, CanvasClosedShapeEnum.Ellipse),
            ("五角星", ScreenShotIcon.STAR, CanvasClosedShapeEnum.Star),
        ]

    def bindCanvasItem(self, canvasItem:CanvasClosedShapeItem, sceneUserNotifyEnum:SceneUserNotifyEnum):
        '''
        绑定操作图元
        @note 存在多种情况

              1. 在选择模式下，各个图元选中切换时，此时各选项采取该图元的实际值来刷新
              2. 刚进入到绘图模式并且首次选择绘图工具，此时绑定图元为None，各选项按默认值初始化
              3. 在选择模式下，操作完当前工具对应图元之后，打算继续绘制新同类图元时，将各选项赋值到新图元上
        '''
        if canvasItem != None:
            self.canvasItem = canvasItem

            if sceneUserNotifyEnum == SceneUserNotifyEnum.SelectItemChangedEvent:
                self.styleMap = self.canvasItem.styleAttribute.getValue().value()

                # QGraphicsItem.opacity()数值范围是：[0, 1]，滑块数值范围设定为：[0, 100]，这里需要转换下
                self.opacity = int(self.canvasItem.opacity() * 100)

                # 更新形状选项
                currentShape = self.styleMap["shape"]
                currentIndex = 0
                for _, _, shapeType in self.shapeTypeInfos:
                    if shapeType == currentShape:
                        break
                    currentIndex = currentIndex + 1 
                    
                self.shapeComBox.setCurrentIndex(currentIndex)
            elif sceneUserNotifyEnum == SceneUserNotifyEnum.StartDrawedEvent:
                self.refreshAttachItem()
        else:
            self.opacity = 100

        self.refreshStyleUI()

    def refreshStyleUI(self):
        pen:QPen = self.styleMap["pen"]
        brush:QBrush = self.styleMap["brush"]
        self.outlineColorPickerButton.setColor(pen.color())
        self.backgroundColorPickerButton.setColor(brush.color())
        self.opacitySlider.setValue(self.opacity)

    def initUI(self):
        self.shapeComBox = self.initShapeOptionUI()
        self.outlineTypeComBox, self.outlineColorPickerButton = self.initOutlineOptionUI()
        self.addSeparator()
        self.backgroundColorPickerButton = self.initColorOptionUI("背景")
        self.addSeparator()
        self.opacitySlider = self.initSliderOptionUI("不透明度")
    
    def outlineTypeComBoxHandle(self, index):
        comBox:ComboBox = self.outlineTypeComBox
        print(f"=====> {comBox.currentData()}")

    def shapeTypeComBoxHandle(self, index):
        comBox:ComboBox = self.shapeComBox
        self.styleMap["shape"] = comBox.currentData()
        self.refreshAttachItem()

    def listenerEvent(self):
        self.outlineColorPickerButton.colorChanged.connect(self.outlineColorChangedHandler)
        self.backgroundColorPickerButton.colorChanged.connect(self.backgroundColorChangedHandler)
        self.opacitySlider.valueChanged.connect(self.opacityValueChangedHandler)

    def refreshAttachItem(self):
        if self.canvasItem != None:
            self.canvasItem.resetStyle(self.styleMap.copy())

    def outlineColorChangedHandler(self, color:QColor):
        pen:QPen = self.styleMap["pen"]        
        pen.setColor(color)

        self.refreshAttachItem()

    def backgroundColorChangedHandler(self, color:QColor):
        brush:QBrush = self.styleMap["brush"]
        brush.setColor(color)

        self.refreshAttachItem()

    def opacityValueChangedHandler(self, value:float):
        self.opacity = value
        if self.canvasItem != None:
            self.canvasItem.setOpacity(self.opacity * 1.0 / 100)

    def initShapeOptionUI(self):
        '''形状选项'''
        shapeComBox = ComboBox(self)
        for text, icon, enum in self.shapeTypeInfos:
            shapeComBox.addItem(text=text, icon=icon, userData=enum)
        shapeComBox.currentIndexChanged.connect(self.shapeTypeComBoxHandle)
        self.initTemplateOptionUI("形状选项", shapeComBox)
        return shapeComBox
    
    def initOutlineOptionUI(self):
        '''描边选项'''

        optionName = "描边"

        # 描边风格选项
        outlineTypeComBox = ComboBox(self)
        for text, enum in self.outlineTypeInfos:
            outlineTypeComBox.addItem(text=text, userData=enum)
        outlineTypeComBox.currentIndexChanged.connect(self.outlineTypeComBoxHandle)

        # 颜色选项
        colorPickerButton = ColorPickerButtonEx(Qt.GlobalColor.yellow, optionName, self, enableAlpha=True)
        colorPickerButton.setCheckable(True)
        colorPickerButton.setFixedSize(30, 30)

        # 布局
        optionView = QWidget()
        optionLayout = QHBoxLayout()
        optionView.setLayout(optionLayout)
        optionLayout.addWidget(QLabel(optionName))
        optionLayout.addWidget(outlineTypeComBox)
        optionLayout.addWidget(colorPickerButton)
        self.addWidget(optionView)

        return outlineTypeComBox, colorPickerButton

    def initColorOptionUI(self, optionName:str):
        '''颜色选项'''
        colorPickerButton = ColorPickerButtonEx(Qt.GlobalColor.yellow, optionName, self, enableAlpha=True)
        colorPickerButton.setCheckable(True)
        colorPickerButton.setFixedSize(30, 30)

        self.initTemplateOptionUI(optionName, colorPickerButton)
        return colorPickerButton

    def initSliderOptionUI(self, optionName:str):
        '''滑块选项'''
        opacitySlider = Slider(Qt.Horizontal)
        opacitySlider.setRange(10, 100)
        opacitySlider.setValue(int(self.opacity * 100))
        self.initTemplateOptionUI(optionName, opacitySlider)
        return opacitySlider

    def initTemplateOptionUI(self, optionName:str, optionWidget:QWidget):
        '''模板选项'''
        optionView = QWidget()
        optionLayout = QHBoxLayout()
        optionView.setLayout(optionLayout)
        optionLayout.addWidget(QLabel(optionName))
        optionLayout.addWidget(optionWidget)
        self.addWidget(optionView)
        return optionWidget

    def createShapeMenu(self, button:PrimarySplitPushButton):
        '''
        @todo 生成一个类似下拉列表的样式，当前实现比较丑陋，后续再改
        '''
        menu = RoundMenu(parent=self)
        menu.setFixedWidth(20)
        menu.addActions([
            Action(ScreenShotIcon.RECTANGLE, "矩形", triggered=lambda c, b=button: self.onMenuClicked(c, b, ScreenShotIcon.RECTANGLE)),
            Action(ScreenShotIcon.CIRCLE, "圆形", triggered=lambda c, b=button: self.onMenuClicked(c, b, ScreenShotIcon.CIRCLE)),
            Action(ScreenShotIcon.STAR, "五角星", triggered=lambda c, b=button: self.onMenuClicked(c, b, ScreenShotIcon.STAR)),
        ])
        return menu

    def onMenuClicked(self, c, button:PrimarySplitPushButton, icon):
        if icon == ScreenShotIcon.RECTANGLE:
            shapeType = CanvasClosedShapeEnum.Rectangle
        elif icon == ScreenShotIcon.CIRCLE:
            shapeType = CanvasClosedShapeEnum.Ellipse
        elif icon == ScreenShotIcon.STAR:
            shapeType = CanvasClosedShapeEnum.Star
        else:
            shapeType = CanvasClosedShapeEnum.Rectangle

        self.styleMap["shape"] = shapeType

        button.setIcon(icon)
        self.refreshAttachItem()        

    def showEvent(self, a0: QShowEvent) -> None:
        self.hBoxLayout.setContentsMargins(1, 1, 1, 1)
        self.setIconSize(QSize(20, 20))
        self.resizeToSuitableWidth()
        self.adjustSize()
        return super().showEvent(a0)

    def switchDrawTool(self, drawActionEnum:DrawActionEnum, cursor:QCursor = Qt.CursorShape.CrossCursor):
        print(f"=======> {drawActionEnum}")