from plugin import *
from qfluentwidgets import (InfoBar, InfoBarPosition, StateToolTip)

class OCRProgressDisplay(PluginInterface):
    @property
    def name(self):
        return "OCRProgressDisplay"

    @property
    def desc(self):
        return "将OCR识别进度显示在UI上"

    def handleEvent(self, eventName, *args, **kwargs):
        if eventName == GlobalEventEnum.OcrStartEvent:
            self.log(f"OCR started {self.name} ===> {self.desc}")
            ocrMode = kwargs["ocr_mode"]
            parentWidget:QWidget = kwargs["parent_widget"]
            if not hasattr(self, "stateTooltip") or self.stateTooltip == None:
                self.stateTooltip = StateToolTip(f'正在OCR识别[{ocrMode}]', '客官请耐心等待哦~~', parentWidget)
                self.stateTooltip.setStyleSheet("background: transparent; border:0px;")
                self.stateTooltip.move(parentWidget.geometry().topRight() + QPoint(-self.stateTooltip.frameSize().width() - 20, self.stateTooltip.frameSize().height() - 20))
                self.stateTooltip.show()
        elif eventName == GlobalEventEnum.OcrEndSuccessEvent:
            self.log("OCR ended")
            if hasattr(self, "stateTooltip") and self.stateTooltip != None:
                self.stateTooltip.setContent('OCR识别已结束')
                self.stateTooltip.setState(True)
                self.stateTooltip = None
        elif eventName == GlobalEventEnum.OcrEndFailEvent:
            self.log("OCR fail")
            parentWidget:QWidget = kwargs["parent_widget"]
            input:str = kwargs["message"]
            if hasattr(self, "stateTooltip") and self.stateTooltip != None:
                InfoBar.error(
                    title='OCR 失败',
                    content=input,
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=-1,    # won't disappear automatically
                    parent=parentWidget,
                )
                self.stateTooltip.setContent('OCR识别失败')
                self.stateTooltip.setState(True)
                self.stateTooltip = None