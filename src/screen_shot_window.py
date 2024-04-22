# coding=utf-8
import os, glob, re
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QSizeF, QPointF, QRectF, QSize, QPoint, QRect

from PyQt5.QtGui import QCursor, QPainter, QColor, QPen, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget
from freezer_window import FreezerWindow
from qfluentwidgets import (RoundMenu, Action, FluentIcon, InfoBar, InfoBarPosition, CommandBarView, Flyout, FlyoutAnimationType, TeachingTip, TeachingTipTailPosition, TeachingTipView)
from canvas_item import *

class ScreenShotWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self._rt_center = QRectF()  # 中央截图区域

        self._pt_start = QPointF()  # 划定截图区域时鼠标左键按下的位置（topLeft）
        self._pt_end = QPointF()  # 划定截图区域时鼠标左键松开的位置（bottomRight）

        self.freeze_imgs:list[FreezerWindow] = []
        self.screenDevicePixelRatio = QApplication.primaryScreen().grabWindow(0).devicePixelRatio()

        startupImagePath, screenX, screenY = self.findScreenImagePath()
        if startupImagePath != None and os.path.exists(startupImagePath):
            imgpix = QPixmap(startupImagePath)
            imgpix.setDevicePixelRatio(self.screenDevicePixelRatio)
            realSize = imgpix.size() / self.screenDevicePixelRatio
            self.addFreezeImg(QPoint(screenX, screenY), realSize,  imgpix)

        actions = [
            Action("贴图", self, triggered=self.tryFreezeImg, shortcut="ctrl+t"),
            Action("取消截图", self, triggered=self.cancelScreenShot, shortcut="esc"),
        ]
        self.addActions(actions)

    def tryFreezeImg(self):
        self.freezeImg(self.addFreezeImg)

    def addFreezeImg(self, screenPoint, cropRect, freezePixmap):
        index = len(self.freeze_imgs)
        self.freeze_imgs.append(FreezerWindow(None, screenPoint, cropRect, freezePixmap, lambda: self.handleFreezeImgClose(index)))
    
    def handleFreezeImgClose(self, index):
        widget:QWidget = self.freeze_imgs[index]
        widget.destroy()
        self.freeze_imgs[index] = None

    # 鼠标穿透策略：优先判断获取焦点窗口的
    def switchMouseThroughState(self):
        focusFreezeWnd:FreezerWindow = None
        screenPos = QCursor.pos()
        for freeze_img in self.freeze_imgs:
            if freeze_img != None and freeze_img.geometry().contains(screenPos):
                focusFreezeWnd = freeze_img
                break
        if focusFreezeWnd != None:
            focusFreezeWnd.switchMouseThroughState()
        else:
            for freeze_img in self.freeze_imgs:
                freeze_img.setMouseThroughState(False)

    def initPainterTool(self):
        self.painter = QPainter()
        self.color_transparent = QtCore.Qt.GlobalColor.transparent
        self.color_black = QColor(0, 0, 0, 64)  # 黑色背景
        self.color_lightBlue = QColor(30, 120, 255, 255)  # 浅蓝色。深蓝色QtCore.Qt.GlobalColor.blue
        self.color_lightWhite = QColor(255, 255, 255, 255)  # 浅蓝色。深蓝色QtCore.Qt.GlobalColor.blue
        self.font_normal = QtGui.QFont('Times New Roman', 11, QtGui.QFont.Weight.Normal)
        self.font_textInput = QtGui.QFont('微软雅黑', 16, QtGui.QFont.Weight.Normal)  # 工具条文字工具默认字体
        self.pen_transparent = QPen(QtCore.Qt.PenStyle.NoPen)  # 没有笔迹，画不出线条
        self.pen_white = QPen(QtCore.Qt.GlobalColor.white)
        self.pen_SolidLine_lightBlue = QPen(self.color_lightBlue)  # 实线，浅蓝色
        self.pen_SolidLine_lightBlue.setStyle(QtCore.Qt.PenStyle.SolidLine)  # 实线SolidLine，虚线DashLine，点线DotLine
        self.pen_SolidLine_lightBlue.setWidthF(4 / self.screenPixmap.devicePixelRatio())  # 0表示线宽为1
        self.pen_SolidLine_lightWhite = QPen(self.color_lightWhite)  # 实线，浅蓝色
        self.pen_SolidLine_lightWhite.setStyle(QtCore.Qt.PenStyle.SolidLine)  # 实线SolidLine，虚线DashLine，点线DotLine
        self.pen_SolidLine_lightWhite.setWidthF(2 / self.screenPixmap.devicePixelRatio())  # 0表示线宽为1
        self.pen_DashLine_lightBlue = QPen(self.color_lightBlue)  # 虚线，浅蓝色
        self.pen_DashLine_lightBlue.setStyle(QtCore.Qt.PenStyle.DashLine)

        self.initMagnifyingGlass()

    def clearScreenShot(self, isGotoScreeShot=True):
        self.hasScreenShot = False  # 是否已通过拖动鼠标左键划定截图区域
        self.isCapturing = False  # 正在拖动鼠标左键选定截图区域时
        self.isMoving = False  # 在截图区域内拖动时
        self.isAdjusting = False  # 在截图区域的边框按住鼠标左键调整大小时
        pos = QPointF()
        self.setCenterArea(pos, pos)
        if isGotoScreeShot:
            self.update()
            self.setCursor(QtCore.Qt.CursorShape.CrossCursor)  # 设置鼠标样式 十字

    def expandScreenShotArea(self, pos):
        '''根据所处的非截图区域的朝向，拓展已划定的截取区域'''
        pt_start, pt_end  = self.getExpandScreenShotArea(pos)
        self.setCenterArea(pt_start, pt_end)
        self.update()

    def reShow(self):
        if self.isActiveWindow():
            return
        finalPixmap, finalGeometry = canvas_util.CanvasUtil.grabScreens()
        self.screenPixmap = finalPixmap
        self.setGeometry(finalGeometry)
        self.initPainterTool()
        self.clearScreenShot()
        self.show()

    def normalizeRectF(self, topLeftPoint, bottomRightPoint):
        return QRectF(topLeftPoint, bottomRightPoint).normalized()

    def centerTopMid(self):
        return self._pt_centerTopMid

    def centerBottomMid(self):
        return self._pt_centerBottomMid

    def centerLeftMid(self):
        return self._pt_centerLeftMid

    def centerRightMid(self):
        return self._pt_centerRightMid

    def setStartPoint(self, pointf, remake=False):
        self._pt_start = pointf
        if remake:
            self.remakeNightArea()

    def setEndPoint(self, pointf, remake=False):
        self._pt_end = pointf
        if remake:
            self.remakeNightArea()

    def setCenterArea(self, start, end):
        self._pt_start = start
        self._pt_end = end
        self.remakeNightArea()

    def remakeNightArea(self):
        '''重新划分九宫格区域。根据中央截图区域计算出来的其他8个区域、截图区域四个边框中点坐标等都是logical的'''
        self._rt_center = self.normalizeRectF(self._pt_start, self._pt_end)
        # 中央区域上下左右边框的中点，用于调整大小
        self._pt_centerTopMid = (self._rt_center.topLeft() + self._rt_center.topRight()) / 2
        self._pt_centerBottomMid = (self._rt_center.bottomLeft() + self._rt_center.bottomRight()) / 2
        self._pt_centerLeftMid = (self._rt_center.topLeft() + self._rt_center.bottomLeft()) / 2
        self._pt_centerRightMid = (self._rt_center.topRight() + self._rt_center.bottomRight()) / 2

        # 以截图区域左上、上中、右上、左中、右中、左下、下中、右下为中心的正方形区域，用于调整大小
        self._square_topLeft = self.squareAreaByCenter(self._rt_center.topLeft())
        self._square_topRight = self.squareAreaByCenter(self._rt_center.topRight())
        self._square_bottomLeft = self.squareAreaByCenter(self._rt_center.bottomLeft())
        self._square_bottomRight = self.squareAreaByCenter(self._rt_center.bottomRight())

        # 挪到四侧边缘操作检测区域，而不是采用边缘中心点的方式
        self._square_topMid = self.squareAreaByHorizontal(self._pt_centerTopMid, self._rt_center.width())
        self._square_bottomMid = self.squareAreaByHorizontal(self._pt_centerBottomMid, self._rt_center.width())
        self._square_leftMid = self.squareAreaByVertical(self._pt_centerLeftMid, self._rt_center.height())
        self._square_rightMid = self.squareAreaByVertical(self._pt_centerRightMid, self._rt_center.height())

        # 除中央截图区域外的8个区域
        self._rt_topLeft = QRectF(self.rect().topLeft(), self._rt_center.topLeft())
        self._rt_top = QRectF(QPointF(self._rt_center.topLeft().x(), 0), self._rt_center.topRight())
        self._rt_topRight = QRectF(QPointF(self._rt_center.topRight().x(), 0), QPointF(self.rect().width(), self._rt_center.topRight().y()))
        self._rt_left = QRectF(QPointF(0, self._rt_center.topLeft().y()), self._rt_center.bottomLeft())
        self._rt_right = QRectF(self._rt_center.topRight(), QPointF(self.rect().width(), self._rt_center.bottomRight().y()))
        self._rt_bottomLeft = QRectF(QPointF(0, self._rt_center.bottomLeft().y()), QPointF(self._rt_center.bottomLeft().x(), self.rect().height()))
        self._rt_bottom = QRectF(self._rt_center.bottomLeft(), QPointF(self._rt_center.bottomRight().x(), self.rect().height()))
        self._rt_bottomRight = QRectF(self._rt_center.bottomRight(), self.rect().bottomRight())

    def squareAreaByCenter(self, pointf):
        '''以QPointF为中心的正方形QRectF'''
        rectf = QRectF(0, 0, 15, 15)
        rectf.moveCenter(pointf)
        return rectf

    def squareAreaByHorizontal(self, pointf, width):
        '''以QPointF为中心的矩形QRectF'''
        rectf = QRectF(0, 0, width, 15)
        rectf.moveCenter(pointf)
        return rectf

    def squareAreaByVertical(self, pointf, height):
        '''以QPointF为中心的矩形QRectF'''
        rectf = QRectF(0, 0, 15, height)
        rectf.moveCenter(pointf)
        return rectf

    def aroundAreaIn8Direction(self):
        '''中央区域周边的8个方向的区域（无交集）'''
        return [self._rt_topLeft, self._rt_top, self._rt_topRight,
                self._rt_left, self._rt_right,
                self._rt_bottomLeft, self._rt_bottom, self._rt_bottomRight]

    def aroundAreaIn4Direction(self):
        '''中央区域周边的4个方向的区域（有交集）
        上区域(左上、上、右上)：0, 0, maxX, topRight.y
        下区域(左下、下、右下)：0, bottomLeft.y, maxX, maxY-bottomLeft.y
        左区域(左上、左、左下)：0, 0, bottomLeft.x, maxY
        右区域(右上、右、右下)：topRight.x, 0, maxX - topRight.x, maxY'''
        pt_topRight = self._rt_center.topRight()
        pt_bottomLeft = self._rt_center.bottomLeft()
        return [QRectF(0, 0, self.rect().width(), pt_topRight.y()),
                QRectF(0, pt_bottomLeft.y(), self.rect().width(), self.rect().height() - pt_bottomLeft.y()),
                QRectF(0, 0, pt_bottomLeft.x(), self.rect().height()),
                QRectF(pt_topRight.x(), 0, self.rect().width() - pt_topRight.x(), self.rect().height())]

    def aroundAreaWithoutIntersection(self):
        '''中央区域周边的4个方向的区域（无交集）
        上区域(左上、上、右上)：0, 0, maxX, topRight.y
        下区域(左下、下、右下)：0, bottomLeft.y, maxX, maxY-bottomLeft.y
        左区域(左)：0, topRight.y, bottomLeft.x-1, center.height
        右区域(右)：topRight.x+1, topRight.y, maxX - topRight.x, center.height'''
        pt_topRight = self._rt_center.topRight()
        pt_bottomLeft = self._rt_center.bottomLeft()
        centerHeight = pt_bottomLeft.y() - pt_topRight.y()
        return [QRectF(0, 0, self.rect().width(), pt_topRight.y()),
                QRectF(0, pt_bottomLeft.y(), self.rect().width(), self.rect().height() - pt_bottomLeft.y()),
                QRectF(0, pt_topRight.y(), pt_bottomLeft.x() - 1, centerHeight),
                QRectF(pt_topRight.x() + 1, pt_topRight.y(), self.rect().width() - pt_topRight.x(), centerHeight)]

    def setBeginDragPoint(self, pointf):
        '''计算开始拖拽位置距离截图区域左上角的向量'''
        self._drag_vector = pointf - self._rt_center.topLeft()

    def getNewPosAfterDrag(self, pointf):
        '''计算拖拽后截图区域左上角的新位置'''
        return pointf - self._drag_vector

    def moveCenterAreaTo(self, pointf):
        '''限制拖拽不能超出屏幕范围'''
        self._rt_center.moveTo(self.getNewPosAfterDrag(pointf))
        startPointF = self._rt_center.topLeft()
        if startPointF.x() < 0:
            self._rt_center.moveTo(0, startPointF.y())
            startPointF = self._rt_center.topLeft()
        if startPointF.y() < 0:
            self._rt_center.moveTo(startPointF.x(), 0)
        endPointF = self._rt_center.bottomRight()
        if endPointF.x() > self.rect().width():
            self._rt_center.moveBottomRight(QPointF(self.rect().width(), endPointF.y()))
            endPointF = self._rt_center.bottomRight()
        if endPointF.y() > self.rect().height():
            self._rt_center.moveBottomRight(QPointF(endPointF.x(), self.rect().height()))
        self.setCenterArea(self._rt_center.topLeft(), self._rt_center.bottomRight())

    def setBeginAdjustPoint(self, pointf):
        '''判断开始调整截图区域大小时鼠标左键在哪个区（不可能是中央区域），用于判断调整大小的意图方向'''
        self._mousePos = self.getMousePosBy(pointf)

    def getMousePosBy(self, pointf):
        if self._square_topLeft.contains(pointf):
            return 'TL'
        elif self._square_topMid.contains(pointf):
            return 'T'
        elif self._square_topRight.contains(pointf):
            return 'TR'
        elif self._square_leftMid.contains(pointf):
            return 'L'
        elif self._rt_center.contains(pointf):
            return 'CENTER'
        elif self._square_rightMid.contains(pointf):
            return 'R'
        elif self._square_bottomLeft.contains(pointf):
            return 'BL'
        elif self._square_bottomMid.contains(pointf):
            return 'B'
        elif self._square_bottomRight.contains(pointf):
            return 'BR'
        else:
            return 'ERROR'
            
    # 获取拓展后的截图起始点和结束点
    def getExpandScreenShotArea(self, pointf):
        pt_start, pt_end = self._pt_start, self._pt_end
        if self._rt_topLeft.contains(pointf):
            pt_start = pointf
        elif self._rt_top.contains(pointf):
            pt_start.setY(pointf.y())
        elif self._rt_topRight.contains(pointf):
            pt_start.setY(pointf.y())
            pt_end.setX(pointf.x())
        elif self._rt_left.contains(pointf):
            pt_start.setX(pointf.x())
        elif self._rt_right.contains(pointf):
            pt_end.setX(pointf.x())
        elif self._rt_bottom.contains(pointf):
            pt_end.setY(pointf.y())
        elif self._rt_bottomLeft.contains(pointf):
            pt_start.setX(pointf.x())
            pt_end.setY(pointf.y())
        elif self._rt_bottomRight.contains(pointf):
            pt_end = pointf
        return pt_start, pt_end

    def adjustCenterAreaBy(self, pointf):
        '''根据开始调整截图区域大小时鼠标左键在哪个区（不可能是中央区域），判断调整大小的意图方向，判定新的开始、结束位置'''
        startPointF = self._rt_center.topLeft()
        endPointF = self._rt_center.bottomRight()
        if self._mousePos == 'TL':
            startPointF = pointf
        elif self._mousePos == 'T':
            startPointF = QPointF(startPointF.x(), pointf.y())
        elif self._mousePos == 'TR':
            startPointF = QPointF(startPointF.x(), pointf.y())
            endPointF = QPointF(pointf.x(), endPointF.y())
        elif self._mousePos == 'L':
            startPointF = QPointF(pointf.x(), startPointF.y())
        elif self._mousePos == 'R':
            endPointF = QPointF(pointf.x(), endPointF.y())
        elif self._mousePos == 'BL':
            startPointF = QPointF(pointf.x(), startPointF.y())
            endPointF = QPointF(endPointF.x(), pointf.y())
        elif self._mousePos == 'B':
            endPointF = QPointF(endPointF.x(), pointf.y())
        elif self._mousePos == 'BR':
            endPointF = pointf
        else:  # 'ERROR'
            return
        newRectF = self.normalizeRectF(startPointF, endPointF)
        self.setCenterArea(newRectF.topLeft(), newRectF.bottomRight())

    def getMouseShapeBy(self, pointf):
        '''根据鼠标位置返回对应的鼠标样式'''
        if self._rt_center.contains(pointf):
            return QtCore.Qt.CursorShape.SizeAllCursor  # 十字有箭头
        elif self._square_topLeft.contains(pointf) or self._square_bottomRight.contains(pointf):
            return QtCore.Qt.CursorShape.SizeFDiagCursor  # ↖↘
        elif self._square_topMid.contains(pointf) or self._square_bottomMid.contains(pointf):
            return QtCore.Qt.CursorShape.SizeVerCursor  # ↑↓
        elif self._square_topRight.contains(pointf) or self._square_bottomLeft.contains(pointf):
            return QtCore.Qt.CursorShape.SizeBDiagCursor  # ↙↗
        elif self._square_leftMid.contains(pointf) or self._square_rightMid.contains(pointf):
            return QtCore.Qt.CursorShape.SizeHorCursor  # ←→
        else:
            return QtCore.Qt.CursorShape.CrossCursor  # 十字无箭头

    def isMousePosInCenterRectF(self, pointf):
        return self._rt_center.contains(pointf)

    def paintCenterArea(self):
        centerRectF = self._rt_center

        '''绘制已选定的截图区域'''
        self.painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)  # 反走样
        # 1.绘制矩形线框
        self.painter.setPen(self.pen_SolidLine_lightBlue)
        self.painter.setBrush(self.color_transparent)
        self.painter.drawRect(centerRectF)

        # 2.绘制矩形线框4个端点和4条边框的中间点
        if centerRectF.width() >= 100 and centerRectF.height() >= 100:
            points = [  # 点坐标
                centerRectF.topLeft(), centerRectF.topRight(), centerRectF.bottomLeft(), centerRectF.bottomRight(),
                self.centerLeftMid(), self.centerRightMid(),
                self.centerTopMid(), self.centerBottomMid()
            ]
            blueDotRadius = QPointF(5*self.screenDevicePixelRatio, 5*self.screenDevicePixelRatio)  # 椭圆蓝点
            # blueDotRadius = QPointF(5, 5)  # 椭圆蓝点
            self.painter.setPen(self.pen_SolidLine_lightWhite)
            self.painter.setBrush(self.color_lightBlue)
            for point in points:
                self.painter.drawEllipse(QRectF(point - blueDotRadius, point + blueDotRadius))

        # 3.在截图区域左上角显示截图区域宽高
        if centerRectF.topLeft().y() > 20:
            labelPos = centerRectF.topLeft() + QPointF(5, -5)
        else:  # 拖拽截图区域到贴近屏幕上边缘时“宽x高”移动到截图区域左上角的下侧
            labelPos = centerRectF.topLeft() + QPointF(5, 15)
        centerPhysicalRect = centerRectF.toRect()
        self.painter.setPen(self.pen_white)
        self.painter.setFont(self.font_normal)
        self.painter.drawText(labelPos, '%s x %s' % (centerPhysicalRect.width(), centerPhysicalRect.height()))
        # 4.在屏幕左上角预览截图结果
        # self.painter.drawPixmap(0, 0, self.centerPhysicalPixmap())  # 从坐标(0, 0)开始绘制

    def paintMaskLayer(self, fullScreen=True):
        if fullScreen:  # 全屏遮罩层
            maskPixmap = QPixmap(self.rect().size())
            maskPixmap.fill(self.color_black)
            self.painter.drawPixmap(0, 0, maskPixmap)
        else:  # 绘制截图区域的周边区域遮罩层，以凸显截图区域
            # 方法一：截图区域以外的8个方向区域
            # for area in self.aroundAreaIn8Direction():
            #     area = area.normalized()
            #     maskPixmap = QPixmap(area.size().toSize())  # 由于float转int的精度问题，可能会存在黑线条缝隙
            #     maskPixmap.fill(self.color_black)
            #     self.painter.drawPixmap(area.topLeft(), maskPixmap)
            # 方法二：截图区域以外的上下左右区域（有交集，交集部分颜色加深，有明显的纵横效果）
            # for area in self.aroundAreaIn4Direction():
            #     maskPixmap = QPixmap(area.size().toSize())
            #     maskPixmap.fill(self.color_black)
            #     self.painter.drawPixmap(area.topLeft(), maskPixmap)
            # 方法三：截图区域以外的上下左右区域（无交集）
            for area in self.aroundAreaWithoutIntersection():
                maskPixmap = QPixmap(area.size().toSize())
                maskPixmap.fill(self.color_black)
                self.painter.drawPixmap(area.topLeft(), maskPixmap)

    def initMagnifyingGlass(self):
        screenPos = QCursor.pos()
        parentPos = self.mapFromGlobal(screenPos)
        localPos:QPoint = self.mapFrom(self, parentPos)
        self.mouse_posX = localPos.x()
        self.mouse_posY = localPos.y()
        self.tool_width = 5

    def paintMagnifyingGlass(self):
        self.painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
        if self.mouse_posX > self.width() - 140:
            enlarge_box_x = self.mouse_posX - 140
        else:
            enlarge_box_x = self.mouse_posX + 20
        if self.mouse_posY > self.height() - 140:
            enlarge_box_y = self.mouse_posY - 120
        else:
            enlarge_box_y = self.mouse_posY + 20
        enlarge_rect = QRect(enlarge_box_x, enlarge_box_y, 120, 120)
        self.painter.drawRect(enlarge_rect)
        self.painter.drawText(enlarge_box_x, enlarge_box_y - 8,
                            '({0}x{1})'.format(self.mouse_posX, self.mouse_posY))
        p = self.screenPixmap
        larger_pix = p.copy(self.mouse_posX - 60, self.mouse_posY - 60, 120, 120).scaled(
            120 + self.tool_width * 10, 120 + self.tool_width * 10)
        pix = larger_pix.copy(int(larger_pix.width() / 2 - 60), int(larger_pix.height() / 2 - 60), 120, 120)
        self.painter.drawPixmap(enlarge_box_x, enlarge_box_y, pix)
        self.painter.setPen(QPen(Qt.green, 1, Qt.SolidLine))
        self.painter.drawLine(enlarge_box_x, enlarge_box_y + 60, enlarge_box_x + 120, enlarge_box_y + 60)
        self.painter.drawLine(enlarge_box_x + 60, enlarge_box_y, enlarge_box_x + 60, enlarge_box_y + 120)

    def paintEvent(self, event):
        canvasPixmap = self.screenPixmap.copy()
        self.painter.begin(canvasPixmap)

        if self.hasScreenShot:
            self.paintMaskLayer(fullScreen=False)  # 绘制截图区域的周边区域遮罩层
            self.paintCenterArea()  # 绘制中央截图区域
        else:
            self.paintMaskLayer()

        self.paintMagnifyingGlass()
        self.painter.end()

        self.painter.begin(self)
        self.painter.drawPixmap(0, 0, canvasPixmap)
        self.painter.end()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            pos = event.pos()
            if self.hasScreenShot:
                if self.isMousePosInCenterRectF(pos):
                    self.isMoving = True  # 进入拖拽移动模式
                    self.setBeginDragPoint(pos)
                else:
                    self.isAdjusting = True  # 进入调整大小模式
                    self.setBeginAdjustPoint(pos)

                    # 如果在非截图区进行点击，那么直接拓展截图区
                    if self._mousePos == "ERROR":
                        self.expandScreenShotArea(pos)
            else:
                self.setCenterArea(pos, pos)
                self.isCapturing = True  # 进入划定截图区域模式
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            self.cancelScreenShot()

    def cancelScreenShot(self):
        if self.hasScreenShot or self.isCapturing:  # 清空已划定的的截图区域
            self.clearScreenShot()
        else:
            self.close()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.isCapturing = False
            self.isMoving = False
            self.isAdjusting = False

            self._pt_start = self._rt_center.topLeft()
            self._pt_end = self._rt_center.bottomRight()

    def mouseMoveEvent(self, event):
        pos = event.pos()
        if self.isVisible():
            self.mouse_posX = pos.x()
            self.mouse_posY = pos.y()
        if self.isCapturing:
            self.hasScreenShot = True
            self.setEndPoint(pos, remake=True)
        elif self.isMoving:
            self.moveCenterAreaTo(pos)
        elif self.isAdjusting:
            self.adjustCenterAreaBy(pos)
        self.update()
        if self.hasScreenShot:
            self.setCursor(self.getMouseShapeBy(pos))
        else:
            self.setCursor(QtCore.Qt.CursorShape.CrossCursor)  # 设置鼠标样式 十字

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            if self.isMousePosInCenterRectF(event.pos()):
                self.close()

    def physicalRectF(self, rectf:QRectF):
        '''计算划定的截图区域的（缩放倍率1.0的）原始矩形（会变大）
        rectf：划定的截图区域的矩形。可为QRect或QRectF'''
        self._pixelRatio = self.screenPixmap.devicePixelRatio()
        return QRectF(rectf.x() * self._pixelRatio, rectf.y() * self._pixelRatio,
                      rectf.width() * self._pixelRatio, rectf.height() * self._pixelRatio)

    def freezeImg(self, callback=None):
        if self._rt_center.size().toSize() != QSize(0, 0):
            cropRect = self.physicalRectF(self._rt_center).toRect()
            centerRect = self._rt_center.toRect()
            freezePixmap = self.screenPixmap.copy(cropRect)
            screenPoint = self.mapToGlobal(centerRect.topLeft())
            self.clearScreenImages()
            freezePixmap.save(self.getScreenImageName(screenPoint), 'png')
            if callback:
                callback(screenPoint, centerRect, freezePixmap)
        self.clearScreenShot(False)
        self.close()

    def clearScreenImages(self):
        filePaths = glob.glob('*.png')
        for filePath in filePaths:
            matchResult = re.match(self.getImageNamePattern(), filePath)
            if len(matchResult.groups()) > 0:
                os.remove(filePath)

    def getScreenImageName(self, screenPoint:QPoint):
        return f'screen {screenPoint.x()}-{screenPoint.y()}.png'

    def getImageNamePattern(self):
        return r'screen ([-]*\d+)-([-]*\d+).png'

    def findScreenImagePath(self):
        # 查找文件后缀名为.png的文件路径
        filePaths = glob.glob('*.png')
        if len(filePaths) > 0:
            # 遍历filePaths中的文件路径
            for filePath in filePaths:
                matchResult = re.match(self.getImageNamePattern(), filePath)

                if matchResult != None:
                    x = int(matchResult.group(1))
                    y = int(matchResult.group(2))
                    return filePath, x, y
        return None, 0, 0
