from plugin import *
from qfluentwidgets import (InfoBar, InfoBarIcon, InfoBarPosition, StateToolTip, FluentIcon as FIF, TransparentToolButton)

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
            if not hasattr(parentWidget, "stateTooltip") or parentWidget.stateTooltip == None:
                parentWidget.stateTooltip = StateToolTip(f'正在OCR识别[{ocrMode}]', '客官请耐心等待哦~~', parentWidget)
                parentWidget.stateTooltip.setStyleSheet("background: transparent; border:0px;")
                parentWidget.stateTooltip.move(parentWidget.geometry().topRight() + QPoint(-parentWidget.stateTooltip.frameSize().width() - 20, parentWidget.stateTooltip.frameSize().height() - 20))
                parentWidget.stateTooltip.show()
        elif eventName == GlobalEventEnum.OcrEndSuccessEvent:
            self.log("OCR ended")
            parentWidget:QWidget = kwargs["parent_widget"]
            if hasattr(parentWidget, "stateTooltip") and parentWidget.stateTooltip != None:
                parentWidget.stateTooltip.setContent('OCR识别已结束')
                parentWidget.stateTooltip.setState(True)
                parentWidget.stateTooltip = None
        elif eventName == GlobalEventEnum.OcrEndFailEvent:
            self.log("OCR fail")
            parentWidget:QWidget = kwargs["parent_widget"]
            input:str = kwargs["message"]
            if hasattr(parentWidget, "stateTooltip") and parentWidget.stateTooltip != None:
                infoBar = InfoBar(
                    icon=InfoBarIcon.ERROR,
                    title='OCR 失败',
                    content=input,
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=-1,    # won't disappear automatically
                    parent=parentWidget,
                )
                copyButton = TransparentToolButton(FIF.COPY, parentWidget)
                copyButton.setFixedSize(36, 36)
                copyButton.setIconSize(QSize(12, 12))
                copyButton.setCursor(Qt.PointingHandCursor)
                copyButton.setVisible(True)
                copyButton.clicked.connect(lambda: self.copyText(infoBar))
                infoBar.addWidget(copyButton)
                infoBar.show()
                parentWidget.stateTooltip.setContent('OCR识别失败')
                parentWidget.stateTooltip.setState(True)
                parentWidget.stateTooltip = None

    def copyText(self, infoBar:InfoBar):
        text = infoBar.contentLabel.text()
        QApplication.clipboard().setText(text)