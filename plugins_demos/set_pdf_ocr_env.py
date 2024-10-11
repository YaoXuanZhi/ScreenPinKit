from plugin import *
from qfluentwidgets import (RoundMenu, Action, StateToolTip)

class SetPdfOcrEnv(PluginInterface):
    @property
    def name(self):
        return "SetPdfOcrEnv"

    @property
    def desc(self):
        return "设置PdfOcr环境"

    def handleEvent(self, eventName, *args, **kwargs):
        if eventName == GlobalEventEnum.OcrStartEvent:
            # os.environ["venv_path"] = "D:/InstallSoftware/Miniconda3/envs/ocrmypdf_env/"
            # os.environ["tesseract_path"] = "D:/OpenSource/ScreenPinKit/deps/Tesseract-OCR"
            # print("修改Pdf-Ocr环境变量成功")
            pass