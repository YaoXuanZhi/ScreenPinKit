import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))
from ocr_loader import *
from PIL import Image
import numpy as np

try:
    from deps.chineseocr_lite.model import OcrHandle
    _importErrorMsg = None
except ImportError as e:
    _importErrorMsg = "\n".join(e.args)

def qpixmapToMatlike(qpixmap:QPixmap):
    # 将 QPixmap 转换为 QImage
    qimage = qpixmap.toImage()

    # # 获取 QImage 的宽度和高度
    # import cv2
    # width = qimage.width()
    # height = qimage.height()

    # # 将 QImage 转换为 numpy 数组
    # byteArray = qimage.bits().asstring(width * height * 4)  # 4 表示每个像素有 4 个字节（RGBA）
    # imageArray = np.frombuffer(byteArray, dtype=np.uint8).reshape((height, width, 4))
    # imageArray = cv2.cvtColor(imageArray, cv2.IMREAD_COLOR)

    image = Image.fromqimage(qimage)
    imageArray = np.array(image)
    return imageArray

class ChineseocrLiteLoader_ReturnText(OcrLoaderInterface):
    def __init__(self):
        self.ocrhandle = None

    @property
    def name(self):
        return "ChineseocrLiteLoader_ReturnText"

    @property
    def displayName(self):
        return "chineseocr_lite-返回Text"

    @property
    def desc(self):
        return "采用chineseocr_lite来进行OCR识别，返回版面分析后的Text"

    @property
    def mode(self):
        return EnumOcrMode.UseOutside

    @property
    def returnType(self):
        return EnumOcrReturnType.Text

    def ocr(self, pixmap:QPixmap):
        boxes, texts, scores = self.__ocr(pixmap)
        width = pixmap.size().width()
        height = pixmap.size().height()
        boxInfos = []
        for i, box in enumerate(boxes):
            text = texts[i]
            score = scores[i]
            boxInfos.append({"box": box, "text": text, "score": score})
        htmlContent = build_svg_html_by_gap_tree_sort(width=width, height=height, box_infos=boxInfos, dpi_scale=CanvasUtil.getDevicePixelRatio())
        return htmlContent

    def __ocr(self, pixmap:QPixmap):
        '''
        调用ocr模块来进行OCR识别
        @note 由于ocr操作耗时较长，该函数会阻塞当前线程
        @bug 本地经过多番尝试，发现只要调用PaddleOCR.ocr()必定会导致程序崩溃，
            无关乎创建多个PaddleOCR对象还是创建多线程来执行都崩，最终采取命令行方式绕过该崩溃
        @later 后续可能会采取内建ocrweb服务的方式来提供，暂时先搁置它
        '''
        if _importErrorMsg != None:
            raise Exception(_importErrorMsg)

        image = Image.fromqpixmap(pixmap)

        short_size = 960

        if self.ocrhandle == None:
            self.ocrhandle = OcrHandle()
        res = self.ocrhandle.text_predict(image, short_size)

        boxes = []
        txts = []
        scores = []

        for info in res:
            rect, text, confidence0 = info
            x1,y1,x2,y2,x3,y3,x4,y4 = rect.reshape(-1)

            left = int(x1)
            top = int(y2)
            right = int(x2)
            bottom = int(y3)

            left_top = [left, top]
            right_top = [right, top]
            right_bottom = [right, bottom]
            left_bottom = [left, bottom]
            boxes.append([left_top, right_top, right_bottom, left_bottom])
            txts.append(text)
            confidence = float(confidence0)
            scores.append(confidence)

        return boxes, txts, scores