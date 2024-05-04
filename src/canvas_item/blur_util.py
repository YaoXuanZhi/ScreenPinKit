from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from scipy.ndimage.filters import gaussian_filter
from qfluentwidgets.common.image_utils import *
# 参考acrylic_label.py控件的实现

class BlurUtil:
    @staticmethod
    def gaussianBlur(pixmap:QPixmap, blurRadius=18, brightFactor=1, blurPicSize= None):
        image = Image.fromqpixmap(pixmap)

        if blurPicSize:
            # adjust image size to reduce computation
            w, h = image.size
            ratio = min(blurPicSize[0] / w, blurPicSize[1] / h)
            w_, h_ = w * ratio, h * ratio

            if w_ < w:
                image = image.resize((int(w_), int(h_)), Image.ANTIALIAS)

        ndArray = np.array(image)

        # handle gray image
        if len(ndArray.shape) == 2:
            ndArray = np.stack([ndArray, ndArray, ndArray], axis=-1)

        # blur each channel
        for i in range(3):
            ndArray[:, :, i] = gaussian_filter(
                ndArray[:, :, i], blurRadius) * brightFactor

        # convert ndarray to QPixmap
        h, w, _ = ndArray.shape
        return QPixmap.fromImage(QImage(ndArray.data, w, h, 3*w, QImage.Format_RGB888))

class BlurCoverThread(QThread):
    """ Blur album cover thread """

    blurFinished = pyqtSignal(QPixmap)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmap = None
        self.blurRadius = 7
        self.maxSize = None

    def run(self):
        if not self.pixmap:
            return

        pixmap = BlurUtil.gaussianBlur(
            self.pixmap, self.blurRadius, 0.85, self.maxSize)
        self.blurFinished.emit(pixmap)

    def blur(self, pixmap: QPixmap, blurRadius=6, maxSize: tuple = None):
        self.pixmap = pixmap
        self.blurRadius = blurRadius
        self.maxSize = maxSize or self.maxSize
        self.start()

class BlurManager(QObject):
    """ Blur Manager """

    _instance = None
    _lastBlurPixmap:QPixmap = None

    # def __new__(cls, *args, **kwargs):
    #     if cls._instance is None:
    #         cls._instance = super(BlurManager, cls).__new__(
    #             cls, *args, **kwargs)
    #         cls._instance.__initialized = False

    #     return cls._instance

    def __init__(self):
        super().__init__()
        # if self.__initialized:
        #     return

        # self.__initialized = True

        self.blurRadius = 15
        self.maxBlurSize = None
        self.blurThread = BlurCoverThread()

    def saveBlurPixmap(self, sourcePixmap):
        self.blurThread.blurFinished.connect(self.__onBlurFinished)
        self.blurThread.blur(sourcePixmap, self.blurRadius, self.maxBlurSize)

    def __onBlurFinished(self, blurPixmap: QPixmap):
        """ blur finished slot """
        self._lastBlurPixmap:QPixmap = blurPixmap

    @property
    def lastBlurPixmap(self) -> QPixmap: return self._lastBlurPixmap