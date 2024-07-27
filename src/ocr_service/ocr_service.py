import os, sys, subprocess, json, codecs
sys.path.insert(0, os.path.join( os.path.dirname(__file__), "..", ".." ))
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import hashlib

try:
    # from paddleocr import PaddleOCR
    # import paddleocr.tools.infer.utility as utility
    IsSupportOcr = True
except ImportError:
    IsSupportOcr = False

from PIL import Image
import numpy as np

class OcrService(QObject):
    def __init__(self, parent: QObject = None) -> None:
        super().__init__(parent)

        try:
            # args = utility.parse_args()
            # self.ocrModel = PaddleOCR(
            #     det_model_dir=args.det_model_dir, 
            #     rec_model_dir=args.rec_model_dir, 
            #     cls_model_dir=args.cls_model_dir, 
            #     rec_char_dict_path=args.rec_char_dict_path,
            #     use_angle_cls=True
            #     )
            self.ocrModel = 1
        except Exception:
            self.ocrModel = None

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
        import time
        ocrRunnerBatPath = os.path.join(workDir, "try_ocr_runner_as_pdf.bat") 
        fullCmd = f"{ocrRunnerBatPath} {input} {output}"
        OcrService.executeSystemCommand(fullCmd)

    def ocr(self, pixmap:QPixmap):
        '''
        调用ocr模块来进行OCR识别
        @note 由于ocr操作耗时较长，该函数会阻塞当前线程
        @bug 本地经过多番尝试，发现只要调用PaddleOCR.ocr()必定会导致程序崩溃，
            无关乎创建多个PaddleOCR对象还是创建多线程来执行都崩，最终采取命令行方式绕过该崩溃
        @later 后续可能会采取内建ocrweb服务的方式来提供，暂时先搁置它
        '''
        if self.ocrModel == None:
            return [], [], []

        image = Image.fromqpixmap(pixmap)
        nd_array = np.asfarray(image)
        result = self.ocrModel.ocr(nd_array, cls=True)
        boxes = [line[0] for line in result]
        txts = [line[1][0] for line in result]
        scores = [line[1][1] for line in result]
        return boxes, txts, scores

    def ocrWithProcess(self, pixmap:QPixmap):
        # return self.ocrWithProcessAsTextMeta(pixmap)
        return self.ocrWithProcessAsPdfName(pixmap)

    def ocrWithProcessAsPdfName(self, pixmap:QPixmap):
        '''
        借用命令行工具来进行OCR识别，并且将识别出来的带文本层的PDF文件名返回
        @note 该函数会阻塞当前线程
        '''
        import time

        workDir = os.path.dirname(__file__)

        hashCode = self.calculateHashForQPixmap(pixmap, 8)
        fileName = f"ocr_{hashCode}"
        ocrTempDirPath = os.path.join(workDir, "ocr_temp")
        if not os.path.exists(ocrTempDirPath):
            os.mkdir(ocrTempDirPath)

        imagePath = os.path.join(ocrTempDirPath, f"{fileName}.png")
        if not os.path.exists(imagePath):
            pixmap.save(imagePath)
            time.sleep(1)

        pdfPath = os.path.join(ocrTempDirPath, f"{fileName}.pdf")
        if not os.path.exists(pdfPath):
            OcrService.image2OcrPdfWithTextLayer(workDir, imagePath, pdfPath)
            time.sleep(1)
        return pdfPath

    def ocrWithProcessAsTextMeta(self, pixmap:QPixmap):
        '''
        借用命令行工具来进行OCR识别，并且结果传递回来
        @note 该函数会阻塞当前线程
        '''
        boxes, txts, scores = [], [], []
        if self.ocrModel == None:
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
            fullCmd = f"{ocrRunnerBatPath} {imagePath}"
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