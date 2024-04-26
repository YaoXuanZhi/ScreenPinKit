from PyQt5.QtCore import *
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
try:
    from paddleocr import PaddleOCR
    import paddleocr.tools.infer.utility as utility
    IsSupportOcr = True
except ImportError:
    IsSupportOcr = False

from PIL import Image
import numpy as np

class OcrService(QObject):
    def __init__(self, parent: QObject = None) -> None:
        super().__init__(parent)

        try:
            args = utility.parse_args()
            self.ocrModel = PaddleOCR(
                det_model_dir=args.det_model_dir, 
                rec_model_dir=args.rec_model_dir, 
                cls_model_dir=args.cls_model_dir, 
                rec_char_dict_path=args.rec_char_dict_path,
                use_angle_cls=True
                )
        except Exception:
            self.ocrModel = None

    def ocr(self, pixmap:QPixmap):
        if self.ocrModel == None:
            return [], [], []

        image = Image.fromqpixmap(pixmap)
        nd_array = np.asfarray(image)
        result = self.ocrModel.ocr(nd_array, cls=True)
        boxes = [line[0] for line in result]
        txts = [line[1][0] for line in result]
        scores = [line[1][1] for line in result]
        return boxes, txts, scores

    @staticmethod
    def isSupported():
        return IsSupportOcr

class OcrThread(QThread):
    ocrStartSignal = pyqtSignal()
    ocrEndSignal = pyqtSignal(list, list, list)
    def __init__(self, action:QAction, pixmap:QPixmap) -> None:
        super().__init__()
        self.action = action
        self.pixmap = pixmap
        
    def run(self):
        self.action(self.pixmap)