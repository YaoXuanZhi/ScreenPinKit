import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))
from ocr_loader import *
from misc import *

class OutsideOcrLoaderAsHtml_ReturnFileName(OcrLoaderInterface):
    @property
    def name(self):
        return "OutsideOcrLoaderAsHtml_ReturnFileName"

    @property
    def displayName(self):
        return "PaddleOCR-返回html文件名"

    @property
    def desc(self):
        return "采用外部OCR来进行OCR识别，返回Tuple"

    @property
    def mode(self):
        return EnumOcrMode.UseOutside

    @property
    def returnType(self):
        return EnumOcrReturnType.FileName

    def image2HtmlWithTextLayer(self, workDir:str, input:str, output:str):
        '''
        将图片转换为带文本层的Html文档
        '''
        ocrRunnerBatPath = os.path.join(workDir, "deps/try_ocr_runner_as_html.bat") 
        dpiScale = CanvasUtil.getDevicePixelRatio()
        fullCmd = f"{ocrRunnerBatPath} {input} {output} {dpiScale}"
        print(fullCmd)
        OsHelper.executeSystemCommand(fullCmd)

    def ocr(self, pixmap:QPixmap):
        '''
        借用命令行工具来进行OCR识别，并且将识别出来的带文本层的Html文件名返回
        @note 该函数会阻塞当前线程
        '''

        workDir = os.path.dirname(__file__)

        hashCode = OsHelper.calculateHashForQPixmap(pixmap, 8)
        fileName = f"ocr_{hashCode}"
        ocrTempDirPath = os.path.join(workDir, "ocr_temp")
        if not os.path.exists(ocrTempDirPath):
            os.mkdir(ocrTempDirPath)

        imagePath = os.path.join(ocrTempDirPath, f"{fileName}.png")
        if not os.path.exists(imagePath):
            pixmap.save(imagePath)

        htmlPath = f"{imagePath}.html"
        try:
            if not os.path.exists(htmlPath):
                self.image2HtmlWithTextLayer(workDir, imagePath, htmlPath)
            return htmlPath
        except Exception as e:
            raise Exception("请检查paddleocr_toolkit的相关运行环境是否配置好了")