from common import ScreenShotIcon
from extend_widgets import *
from canvas_item import *
from .canvas_item_toolbar import *

class TextEditToolbar(CanvasItemToolBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.listenerEvent()

    def initDefaultStyle(self):
        self.opacity:int = 100
        defaultFont = QFont()
        defaultFont.setPointSize(16)
        self.styleMap = {
            "font" : defaultFont,
            "textColor" : QColor(Qt.GlobalColor.red),
        }

    def initUI(self):
        self.boldButton = self.addAction(Action(ScreenShotIcon.TEXT_BOLD, '加粗', triggered=self.fontExtStyleChangedHandler))
        self.boldButton.setCheckable(True)
        self.italicButton = self.addAction(Action(ScreenShotIcon.TEXT_ITALIC, '斜体', triggered=self.fontExtStyleChangedHandler))
        self.italicButton.setCheckable(True)
        self.textColorPickerButton = self.initColorOptionUI("颜色", self.styleMap["textColor"])
        self.fontPickerButton = self.initFontOptionUI("字体", self.styleMap["font"])
        self.addSeparator()
        self.opacitySlider = self.initSliderOptionUI("不透明度", self.opacity, 10, 100)

    def fontExtStyleChangedHandler(self):
        font:QFont = self.styleMap["font"]
        font.setBold(self.boldButton.isChecked())
        font.setItalic(self.italicButton.isChecked())

        self.fontPickerButton.setTargetFont(font)

        self.refreshAttachItem()

    def refreshStyleUI(self):
        font:QFont = self.styleMap["font"]
        textColor:QColor = self.styleMap["textColor"]
        self.boldButton.setChecked(font.bold())
        self.italicButton.setChecked(font.italic())
        self.opacitySlider.setValue(self.opacity)
        self.textColorPickerButton.setColor(textColor)
        self.fontPickerButton.setTargetFont(font)

    def textColorChangedHandler(self, color:QColor):
        self.styleMap["textColor"] = color
        self.refreshAttachItem()

    def fontChangedHandler(self, font:QFont):
        self.styleMap["font"] = font
        self.refreshAttachItem()

    def opacityValueChangedHandler(self, value:float):
        self.opacity = value
        if self.canvasItem != None:
            self.canvasItem.setOpacity(self.opacity * 1.0 / 100)

    def listenerEvent(self):
        self.textColorPickerButton.colorChanged.connect(self.textColorChangedHandler)
        self.fontPickerButton.fontChanged.connect(self.fontChangedHandler)
        self.opacitySlider.valueChanged.connect(self.opacityValueChangedHandler)

    def refreshAttachItem(self):
        if self.canvasItem != None:
            self.canvasItem.setOpacity(self.opacity * 1.0 / 100)
            self.canvasItem.resetStyle(self.styleMap.copy())

    def onWheelZoom(self, angleDelta:int):
        finalFont:QFont = self.styleMap["font"]

        # 自定义滚轮事件的行为
        finalFontSize = finalFont.pointSize()
        if angleDelta > 1:
            # 放大
            finalFontSize = finalFontSize + 2
        else:
            # 缩小
            finalFontSize = max(1, finalFontSize - 2)
        finalFont.setPointSize(finalFontSize)
        self.styleMap["font"] = finalFont

    def bindCanvasItem(self, canvasItem:CanvasTextItem, sceneUserNotifyEnum:SceneUserNotifyEnum):
        '''
        绑定操作图元
        @note 存在多种情况

              1. 在选择模式下，各个图元选中切换时，此时各选项采取该图元的实际值来刷新
              2. 刚进入到绘图模式并且首次选择绘图工具，此时绑定图元为None，各选项按默认值初始化
              3. 在选择模式下，操作完当前工具对应图元之后，打算继续绘制新同类图元时，将各选项赋值到新图元上
        '''
        if canvasItem != None:
            if self.canvasItem != None:
                self.canvasItem.setWheelEventCallBack(None)
            self.canvasItem = canvasItem

            if sceneUserNotifyEnum == SceneUserNotifyEnum.SelectItemChangedEvent:
                self.canvasItem.setWheelEventCallBack(self.onWheelZoom)
                self.styleMap = self.canvasItem.styleAttribute.getValue().value()

                # QGraphicsItem.opacity()数值范围是：[0, 1]，滑块数值范围设定为：[0, 100]，这里需要转换下
                self.opacity = int(self.canvasItem.opacity() * 100)
                self.selectItemChangedHandle(self.canvasItem)
            elif sceneUserNotifyEnum == SceneUserNotifyEnum.StartDrawedEvent:
                self.refreshAttachItem()
        else:
            self.opacity = 100

        self.refreshStyleUI()