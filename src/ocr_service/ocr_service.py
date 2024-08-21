import os, sys, subprocess, json, codecs
sys.path.insert(0, os.path.join( os.path.dirname(__file__), "."))
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from canvas_item import CanvasUtil
from enum import Enum
import hashlib
from PIL import Image
import numpy as np

class EnumOcrMode(Enum):
    NoSupport = 0
    '''不支持'''

    UseInside = 1
    '''内部OCR模块'''

    UseOutside = 2
    '''外部OCR模块'''

try:
    from PaddleOCRModel.PaddleOCRModel import det_rec_functions as OcrDetector
    _currentOcrMode = EnumOcrMode.UseInside
except ImportError:
    _currentOcrMode = EnumOcrMode.UseOutside

class OcrService(QObject):
    def __init__(self, parent: QObject = None) -> None:
        super().__init__(parent)

    def calculateHashForQPixmap(self, pixmap:QPixmap, cutLength=0, hashAlgorithm="sha256"):
        '''计算QPixmap的哈希值，根据需要可以截取对应哈希结果长度'''
        byteArray = Image.fromqpixmap(pixmap).tobytes()

        # 创建哈希对象
        hashObj = hashlib.new(hashAlgorithm)

        # 更新哈希对象
        hashObj.update(byteArray)

        # 获取哈希值的十六进制表示
        if cutLength > 0:
            result = hashObj.hexdigest()[0:cutLength]
        else:
            result = hashObj.hexdigest()

        return result

    @staticmethod
    def image2OcrPdfWithTextLayer(workDir:str, input:str, output:str):
        '''
        将图片转换为带文本层的PDF文档

        使用OCRmyPDF实现，其内部使用img2pdf会将图片转换为pdf再进行OCR识别
        '''
        ocrRunnerBatPath = os.path.join(workDir, "try_ocr_runner_as_pdf.bat") 
        fullCmd = f"{ocrRunnerBatPath} {input} {output}"
        OcrService.executeSystemCommand(fullCmd)

    @staticmethod
    def image2HtmlWithTextLayer(workDir:str, input:str, output:str):
        '''
        将图片转换为带文本层的Html文档
        '''
        ocrRunnerBatPath = os.path.join(workDir, "try_ocr_runner_as_html.bat") 
        # ocrRunnerBatPath = os.path.join(workDir, "try_ocr_runner_as_svghtml_test.bat") 
        dpiScale = CanvasUtil.getDevicePixelRatio()
        fullCmd = f"{ocrRunnerBatPath} {input} {output} {dpiScale}"
        OcrService.executeSystemCommand(fullCmd)

    @staticmethod
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

    def ocr(self, pixmap:QPixmap):
        '''
        调用ocr模块来进行OCR识别
        @note 由于ocr操作耗时较长，该函数会阻塞当前线程
        @bug 本地经过多番尝试，发现只要调用PaddleOCR.ocr()必定会导致程序崩溃，
            无关乎创建多个PaddleOCR对象还是创建多线程来执行都崩，最终采取命令行方式绕过该崩溃
        @later 后续可能会采取内建ocrweb服务的方式来提供，暂时先搁置它
        '''
        if OcrService.mode() == EnumOcrMode.NoSupport:
            return [], [], []

        matlike = OcrService.qpixmapToMatlike(pixmap)

        ocr_sys = OcrDetector(matlike, use_dnn = False, version=3)# 支持v2和v3版本的
        dt_boxes = ocr_sys.get_boxes()
        results, results_info = ocr_sys.recognition_img(dt_boxes)
        match_text_boxes = ocr_sys.get_match_text_boxes(dt_boxes[0], results)

        boxes = []
        txts = []
        scores = []

        for info in match_text_boxes:
            text = info['text']
            left = float(info['box'][0][0])
            top = float(info['box'][0][1])
            right = float(info['box'][1][0])
            bottom = float(info['box'][2][1])

            left_top = [left, top]
            right_top = [right, top]
            right_bottom = [right, bottom]
            left_bottom = [left, bottom]
            boxes.append([left_top, right_top, right_bottom, left_bottom])
            txts.append(text)
            scores.append(0.97)

        return boxes, txts, scores

    def ocrWithProcessOutSide(self, pixmap:QPixmap):
        '''调用外部进程进行OCR'''
        # return self.ocrWithProcessAsTextMeta(pixmap)
        return self.ocrWithProcessAsPdf(pixmap)
        # return self.ocrWithProcessAsHtml(pixmap)

    def ocrWithProcessAsPdf(self, pixmap:QPixmap):
        '''
        借用命令行工具来进行OCR识别，并且将识别出来的带文本层的PDF文件名返回
        @note 该函数会阻塞当前线程
        '''

        workDir = os.path.dirname(__file__)

        hashCode = self.calculateHashForQPixmap(pixmap, 8)
        fileName = f"ocr_{hashCode}"
        ocrTempDirPath = os.path.join(workDir, "ocr_temp")
        if not os.path.exists(ocrTempDirPath):
            os.mkdir(ocrTempDirPath)

        imagePath = os.path.join(ocrTempDirPath, f"{fileName}.png")
        if not os.path.exists(imagePath):
            pixmap.save(imagePath)

        pdfPath = os.path.join(ocrTempDirPath, f"{fileName}.pdf")
        if not os.path.exists(pdfPath):
            OcrService.image2OcrPdfWithTextLayer(workDir, imagePath, pdfPath)

        return pdfPath

    def ocrWithProcessAsTextMeta(self, pixmap:QPixmap):
        '''
        借用命令行工具来进行OCR识别，并且结果传递回来
        @note 该函数会阻塞当前线程
        '''
        boxes, txts, scores = [], [], []
        if OcrService.mode() == EnumOcrMode.NoSupport:
            return boxes, txts, scores

        workDir = os.path.dirname(__file__)

        hashCode = self.calculateHashForQPixmap(pixmap, 8)
        fileName = f"ocr_{hashCode}"
        ocrTempDirPath = os.path.join(workDir, "ocr_temp")
        if not os.path.exists(ocrTempDirPath):
            os.mkdir(ocrTempDirPath)

        imagePath = os.path.join(ocrTempDirPath, f"{fileName}.png")
        if not os.path.exists(imagePath):
            pixmap.save(imagePath)

        ocrResultPath = f"{imagePath}.ocr"
        if not os.path.exists(ocrResultPath):
            ocrRunnerBatPath = os.path.join(workDir, "try_ocr_runner.bat") 
            # ocrRunnerBatPath = os.path.join(workDir, "try_tessact_ocr_runner.bat") 
            fullCmd = f"{ocrRunnerBatPath} {imagePath} {ocrResultPath}"
            OcrService.executeSystemCommand(fullCmd)

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

    def ocrWithProcessAsHtml(self, pixmap:QPixmap):
        '''
        借用命令行工具来进行OCR识别，并且将识别出来的带文本层的Html文件名返回
        @note 该函数会阻塞当前线程
        '''

        workDir = os.path.dirname(__file__)

        hashCode = self.calculateHashForQPixmap(pixmap, 8)
        fileName = f"ocr_{hashCode}"
        ocrTempDirPath = os.path.join(workDir, "ocr_temp")
        if not os.path.exists(ocrTempDirPath):
            os.mkdir(ocrTempDirPath)

        imagePath = os.path.join(ocrTempDirPath, f"{fileName}.png")
        if not os.path.exists(imagePath):
            pixmap.save(imagePath)

        htmlPath = f"{imagePath}.html"
        if not os.path.exists(htmlPath):
            OcrService.image2HtmlWithTextLayer(workDir, imagePath, htmlPath)

        return htmlPath

    @staticmethod
    def executeSystemCommand(cmd):
        '''
        执行系统shell命令的函数
        @note: 该函数会阻塞当前线程
        '''
        try:
            result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=os.environ, encoding='utf-8')
            output = result.stdout
            print("Command Result:\n", output)
        except subprocess.CalledProcessError as e:
            # 如果命令执行出错，打印错误信息
            print("An error occurred while executing the command.", e)

    @staticmethod
    def mode():
        return _currentOcrMode
        # return EnumOcrMode.UseOutSide

class OcrThread(QThread):
    ocrStartSignal = pyqtSignal()
    ocrEndSignal = pyqtSignal(list, list, list)
    def __init__(self, action:QAction, pixmap:QPixmap) -> None:
        super().__init__()
        self.action = action
        self.pixmap = pixmap
        
    def run(self):
        self.action(self.pixmap)