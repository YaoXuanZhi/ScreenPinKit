from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import *
from icon import ScreenShotIcon
from .color_picker_button_plus import *
from .font_picker_button_plus import *
from canvas_item import *
from .canvas_item_toolbar import *

class BlurToolbar(CommandBarView):
    blurTypeChangedSignal = pyqtSignal(DrawActionEnum)
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.initUI()

    def initUI(self):
        eraseActions = [
            Action(ScreenShotIcon.MOSAIC, '马赛克', triggered=lambda: self.blurTypeChangedSignal.emit(DrawActionEnum.Mosaic)),
            Action(ScreenShotIcon.RECTANGLE, '模糊', triggered=lambda: self.blurTypeChangedSignal.emit(DrawActionEnum.UseEraserRectItem)),
            ]

        self.actionGroup = QActionGroup(self)
        for action in eraseActions:
            action.setCheckable(True)
            self.actionGroup.addAction(action)
        
        self.addActions(eraseActions)

        self.strengthSlider = self.initSliderOptionUI("强度", 50, 10, 100)

    def initSliderOptionUI(self, optionName:str, defaultValue:int = 0, minValue:int = 0, maxValue:int = 100):
        '''滑块选项'''
        opacitySlider = Slider(Qt.Horizontal)
        opacitySlider.setRange(minValue, maxValue)
        opacitySlider.setValue(defaultValue)
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

    def showEvent(self, a0: QShowEvent) -> None:
        self.hBoxLayout.setContentsMargins(1, 1, 1, 1)
        self.setIconSize(QSize(20, 20))
        self.resizeToSuitableWidth()
        self.adjustSize()
        return super().showEvent(a0)