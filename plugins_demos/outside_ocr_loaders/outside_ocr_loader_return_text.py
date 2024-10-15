import os, sys, codecs, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))
from ocr_loader import *
from misc import *

class OutsideOcrLoader_ReturnText(OcrLoaderInterface):
    @property
    def name(self):
        return "OutsideOcrLoader_ReturnText"

    @property
    def displayName(self):
        return "PaddleOCR-返回文本"

    @property
    def desc(self):
        return "采用外部OCR来进行OCR识别，返回Text"

    @property
    def mode(self):
        return EnumOcrMode.UseOutside

    @property
    def returnType(self):
        return EnumOcrReturnType.Text

    def ocr(self, pixmap:QPixmap):
        try:
            boxes, txts, scores = self.__ocr(pixmap)
            width = pixmap.size().width()
            height = pixmap.size().height()
            dpiScale = pixmap.devicePixelRatioF()
            htmlContent = build_svg_html(width=width, height=height, boxes=boxes, txts=txts, dpi_scale=dpiScale)
            return htmlContent
        except Exception as e:
            raise Exception(f"请检查paddleocr_toolkit的相关运行环境是否配置好了 {e}")

    def __ocr(self, pixmap:QPixmap):
        '''
        借用命令行工具来进行OCR识别，并且结果传递回来
        @note 该函数会阻塞当前线程
        '''
        boxes, txts, scores = [], [], []
        workDir = os.path.dirname(__file__)

        hashCode = OsHelper.calculateHashForQPixmap(pixmap, 8)
        fileName = f"ocr_{hashCode}"
        ocrTempDirPath = os.path.join(workDir, "ocr_temp")
        if not os.path.exists(ocrTempDirPath):
            os.mkdir(ocrTempDirPath)

        imagePath = os.path.join(ocrTempDirPath, f"{fileName}.png")
        if not os.path.exists(imagePath):
            pixmap.save(imagePath)

        ocrResultPath = f"{imagePath}.ocr"
        if not os.path.exists(ocrResultPath):
            ocrRunnerBatPath = os.path.join(workDir, "deps/try_paddle_ocr_runner.bat") 
            # ocrRunnerBatPath = os.path.join(workDir, "deps/try_tessact_ocr_runner.bat") 
            fullCmd = f"{ocrRunnerBatPath} {imagePath} {ocrResultPath}"
            OsHelper.executeSystemCommand(fullCmd)

        # 读取缓存文件夹上的ocr识别结果 
        if os.path.exists(ocrResultPath):
            with codecs.open(ocrResultPath, mode="r", encoding="utf-8", errors='ignore') as f:
                json_str = f.read()
                ocrResult = json.loads(json_str)

                boxes = json.loads(ocrResult["boxes"])
                txts = json.loads(ocrResult["txts"])
                scores = json.loads(ocrResult["scores"])
                f.close()

        # if os.path.exists(imagePath):
        #     os.remove(imagePath)
        # if os.path.exists(ocrResultPath):
        #     os.remove(ocrResultPath)

        return boxes, txts, scores