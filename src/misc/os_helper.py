import os, subprocess, hashlib
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PIL import Image
import numpy as np

class OsHelper:
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
            raise e

    @staticmethod
    def calculateHashForQPixmap(pixmap:QPixmap, cutLength=0, hashAlgorithm="sha256"):
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