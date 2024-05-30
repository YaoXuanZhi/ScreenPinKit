# coding=utf-8
from enum import Enum
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PIL import ImageFilter, Image

class AfterEffectType(Enum):
    '''
    图像后处理效果类型
    '''
    GaussianBlur = "高斯模糊"
    Mosaic = "马赛克"

class AfterEffectUtilByPIL:
    '''
    基于PIL实现的图像后处理效果
    '''
    @staticmethod
    def gaussianBlur(pixmap:QPixmap, blurRadius = 5):
        '''高斯模糊'''
        return AfterEffectUtilByPIL.effectUtilByPIL(pixmap, ImageFilter.GaussianBlur(radius=blurRadius))

    @staticmethod
    def mosaic(pixmap:QPixmap, blockSize = 2, pixelateFactor = 1):
        '''
        马赛克效果
        由于那种逐个像素遍历的处理太低效了，最终采取了网友分享的思路：
        https://blog.csdn.net/qq_38563206/article/details/136030277
        '''
        width = pixmap.width()
        height = pixmap.height()
        tempImage = pixmap.toImage()
        if tempImage.format() != QImage.Format.Format_RGB32:
            tempImage = tempImage.convertToFormat(QImage.Format.Format_RGB32)

        image = Image.fromqimage(tempImage)
    
        # 计算图像的宽度和高度
        width, height = image.size
    
        # 计算马赛克块的数量
        num_blocks_width = max(width // blockSize, 1)
        num_blocks_height = max(height // blockSize, 1)
    
        # 缩小图像，创建马赛克效果
        blockSourceImage = image.resize((num_blocks_width, num_blocks_height))
        # 放大图像，增加马赛克强度
        finalImage = blockSourceImage.resize((width // pixelateFactor, height // pixelateFactor), Image.NEAREST)
        finalImage = finalImage.resize((width, height), Image.NEAREST)
        return QPixmap.fromImage(QImage(finalImage.tobytes(), width, height, 3*width, QImage.Format.Format_RGB888))

    # @staticmethod
    # def mosaic2(pixmap:QPixmap, blockSize = 16):
    #     '''马赛克效果(效率太低，废弃)'''
    #     width = pixmap.width()
    #     height = pixmap.height()
    #     tempImage = pixmap.toImage()
    #     if tempImage.format() != QImage.Format.Format_RGB32:
    #         tempImage = tempImage.convertToFormat(QImage.Format.Format_RGB32)

    #     image = Image.fromqimage(tempImage)

    #     # finalImage = image.copy()
    #     finalImage = Image.new("RGB", (width, height), (0, 0, 0))
    #     # 在新的图片上绘制马赛克块
    #     draw = ImageDraw.Draw(finalImage)
    #     # 循环遍历图片中的每个块
    #     for x in range(0, width, blockSize):
    #         for y in range(0, height, blockSize):
    #             # 截取当前块的区域
    #             box = (x, y, x+blockSize, y+blockSize)
    #             block = image.crop(box)
    #             # 计算当前块的平均颜色
    #             r, g, b = block.resize((1, 1)).getpixel((0, 0))
    #             color = (r, g, b)
    #             draw.rectangle(box, fill=color)

    #     return QPixmap.fromImage(QImage(finalImage.tobytes(), width, height, 3*width, QImage.Format.Format_RGB888))

    @staticmethod
    def effectUtilByPIL(pixmap:QPixmap, effectFilter:ImageFilter.MultibandFilter):
        '''
        PIL图像处理
        这篇博客介绍得比较完整：https://www.cnblogs.com/traditional/p/11111770.html
        '''
        width = pixmap.width()
        height = pixmap.height()
        tempImage = pixmap.toImage()
        if tempImage.format() != QImage.Format.Format_RGB32:
            tempImage = tempImage.convertToFormat(QImage.Format.Format_RGB32)

        image = Image.fromqimage(tempImage)

        # 图像处理
        finalImage =  image.filter(effectFilter)

        return QPixmap.fromImage(QImage(finalImage.tobytes(), width, height, 3*width, QImage.Format.Format_RGB888))

    @staticmethod
    def effectDemos(pixmap:QPixmap):
        # 图像模糊
        # return ImageEffectUtil.effectUtilByPIL(pixmap, ImageFilter.BLUR)

        # 图像突出
        # return ImageEffectUtil.effectUtilByPIL(pixmap, ImageFilter.DETAIL)

        # 边缘提取
        # return ImageEffectUtil.effectUtilByPIL(pixmap, ImageFilter.FIND_EDGES)

        # 轮廓提取
        return AfterEffectUtilByPIL.effectUtilByPIL(pixmap, ImageFilter.CONTOUR)

# class AfterEffectUtilByCv:
#     '''
#     基于OpenCv实现的图像后处理效果，依赖重遂放弃
#     '''
#     @staticmethod
#     def gaussianBlur(pixmap:QPixmap, blurRadius=5):
#         return AfterEffectUtilByCv.gaussianBlurEffectByCv(pixmap, blurRadius)

#     def mosaic(pixmap:QPixmap, blockSize=3):
#         return AfterEffectUtilByCv.mosaicEffectByCv(pixmap, blockSize)

#     @staticmethod
#     def _mosaicEffectByCv(ndArray:np.ndarray, x, y, w, h, neighbor=2):
#         import cv2
#         fh, fw = ndArray.shape[0], ndArray.shape[1]
#         if (y + h > fh) or (x + w > fw):
#             return
#         for i in range(0, h - neighbor, neighbor):  # 关键点0 减去neightbour 防止溢出
#             for j in range(0, w - neighbor, neighbor):
#                 rect = [j + x, i + y, neighbor, neighbor]
#                 color = ndArray[i + y][j + x].tolist()  # 关键点1 tolist
#                 left_up = (rect[0], rect[1])
#                 right_down = (rect[0] + neighbor - 1, rect[1] + neighbor - 1)  # 关键点2 减去一个像素
#                 cv2.rectangle(ndArray, left_up, right_down, color, -1)

#     @staticmethod
#     def mosaicEffectByCv(pixmap:QPixmap, blockSize = 3):
#         '''马赛克效果'''
#         tempImage = pixmap.toImage()
#         if tempImage.format() != QImage.Format.Format_RGB32:
#             tempImage = tempImage.convertToFormat(QImage.Format.Format_RGB32)

#         image = Image.fromqimage(tempImage)
#         width, height = pixmap.width(), pixmap.height()
#         ndArray = np.array(image)

#         AfterEffectUtilByCv._mosaicEffectByCv(ndArray, 0, 0, width, height, blockSize)
    
#         return QPixmap.fromImage(QImage(ndArray, width, height, 3*width, QImage.Format.Format_RGB888))

#     @staticmethod
#     def gaussianBlurEffectByCv(pixmap:QPixmap, blurRadius=5):
#         import cv2
#         '''高斯模糊效果'''
#         tempImage = pixmap.toImage()
#         if tempImage.format() != QImage.Format.Format_RGB32:
#             tempImage = tempImage.convertToFormat(QImage.Format.Format_RGB32)

#         image = Image.fromqimage(tempImage)
#         width, height = pixmap.width(), pixmap.height()
#         ndArray = np.array(image)

#         blurred = cv2.GaussianBlur(ndArray, (blurRadius, blurRadius), 0)
#         return QPixmap.fromImage(QImage(blurred.data, width, height, 3*width, QImage.Format.Format_RGB888))

class BlurEffectThread(QThread):
    """ 
    Blur album cover thread
    参考acrylic_label.py控件的实现，实现后处理缓存机制
    """

    blurFinished = pyqtSignal(QPixmap)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmap = None
        self.blurRadius = 7
        self.maxSize = None

    def run(self):
        if not self.pixmap:
            return

        # pixmap = AfterEffectUtilByCv.gaussianBlur(
        #     self.pixmap, self.blurRadius)

        pixmap = AfterEffectUtilByPIL.gaussianBlur(
            self.pixmap, self.blurRadius)
        self.blurFinished.emit(pixmap)

    def blur(self, pixmap: QPixmap, blurRadius=6, maxSize: tuple = None):
        self.pixmap = pixmap
        self.blurRadius = blurRadius
        self.maxSize = maxSize or self.maxSize
        self.start()

class PixmapCacheManager(QObject):
    """ PixmapCache Manager """

    _lastPixmap:QPixmap = None

    def __init__(self):
        super().__init__()

    def saveLastPixmap(self, sourcePixmap):
        self._lastPixmap = sourcePixmap

    @property
    def lastPixmap(self) -> QPixmap: return self._lastPixmap

class EffectWorker(QThread):
    '''图像后处理线程'''
    effectFinishedSignal = pyqtSignal(QPixmap)
    isRunning = 0

    def __init__(self, effectType:AfterEffectType) -> None:
        super().__init__()
        self.setStackSize(1024*1024)
        self.effectType = effectType

    def startEffect(self, sourcePixmap:QPixmap, strength:int):
        if self.isRunning:
            return
        self.sourcePixmap = sourcePixmap
        self.strength = strength
        self.start()

    def run(self):
        self.isRunning = 1
        try:
            if self.effectType == AfterEffectType.GaussianBlur:
                finalPixmap = AfterEffectUtilByPIL.gaussianBlur(self.sourcePixmap, self.strength)
                pass
            elif self.effectType == AfterEffectType.Mosaic:
                finalPixmap = AfterEffectUtilByPIL.mosaic(self.sourcePixmap, 5, self.strength)
            else:
                pass
            self.effectFinishedSignal.emit(finalPixmap)
            self.isRunning = 0
        except Exception as e:
            print(e)
            self.isRunning = 0
            raise