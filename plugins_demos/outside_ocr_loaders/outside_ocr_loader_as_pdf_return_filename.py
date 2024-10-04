'''
## 部署ocrmypdf
## 安装choco
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

## 通过choco安装其它依赖
choco install --pre tesseract
choco install ghostscript
choco install pngquant
'''
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))
from ocr_loader import *
from misc import *

class OutsideOcrLoaderAsPdf_ReturnFileName(OcrLoaderInterface):
    @property
    def name(self):
        return "OutsideOcrLoaderAsPdf_ReturnFileName"

    @property
    def desc(self):
        return "采用外部OCR来进行OCR识别，返回FileName"

    @property
    def mode(self):
        return EnumOcrMode.UseOutside

    @property
    def returnType(self):
        return EnumOcrReturnType.FileName

    def image2OcrPdfWithTextLayer(self, workDir:str, input:str, output:str):
        '''
        将图片转换为带文本层的PDF文档

        使用OCRmyPDF实现，其内部使用img2pdf会将图片转换为pdf再进行OCR识别
        '''
        ocrRunnerBatPath = os.path.join(workDir, "deps/try_ocr_runner_as_pdf.bat") 
        fullCmd = f"{ocrRunnerBatPath} {input} {output}"
        OsHelper.executeSystemCommand(fullCmd)

    def ocr(self, pixmap:QPixmap):
        '''
        借用命令行工具来进行OCR识别，并且将识别出来的带文本层的PDF文件名返回
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

        pdfPath = os.path.join(ocrTempDirPath, f"{fileName}.pdf")
        if not os.path.exists(pdfPath):
            self.image2OcrPdfWithTextLayer(workDir, imagePath, pdfPath)

        return pdfPath
