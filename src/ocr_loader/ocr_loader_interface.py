from enum import Enum
from abc import ABC, abstractmethod
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class EnumOcrMode(Enum):
    '''OCR模式'''

    NoSupport = 0
    '''不支持'''

    UseInside = 1
    '''内部OCR模块'''

    UseOutside = 2
    '''外部OCR模块'''

class EnumOcrReturnType(Enum):
    '''OCR结果返回类型'''

    Text = 1
    '''OCR结果之后返回文本'''

    FileName = 2
    '''OCR结果之后返回临时文件名'''

    Tuple = 3
    '''OCR结果之后返回Tuple'''

class OcrLoaderInterface(ABC):
    @property
    @abstractmethod
    def name(self):
        return "name"

    @property
    @abstractmethod
    def desc(self):
        return "desc"

    @property
    @abstractmethod
    def mode(self):
        return EnumOcrMode.NoSupport

    @property
    @abstractmethod
    def returnType(self):
        return EnumOcrReturnType.Text

    @abstractmethod
    def ocr(self, image:QPixmap):
        return "ocr result"