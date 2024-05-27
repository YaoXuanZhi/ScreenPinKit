# coding=utf-8
from canvas_item import *

class ScreenShotWindow(QWidget):
    snipedSignal = pyqtSignal(QPoint, QSize, QPixmap)
    closedSignal = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.defaultFlag()

        self._pt_start = QPointF()  # 划定截图区域时鼠标左键按下的位置（topLeft）
        self._pt_end = QPointF()  # 划定截图区域时鼠标左键松开的位置（bottomRight）
        self.initPainterTool()
        self.initActions()
        # self.setWindowOpacity(0.5)

    def initActions(self):
        actions = [
            QAction(parent=self, triggered=self.copyToClipboard, shortcut="ctrl+c"),
            QAction(parent=self, triggered=self.snip, shortcut="ctrl+t"),
            QAction(parent=self, triggered=self.cancelScreenShot, shortcut="esc"),
        ]
        self.addActions(actions)

    def defaultFlag(self):
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)

    def copyToClipboard(self):
        cropRect = self.normalizeRectF(self._pt_start, self._pt_end)
        realCropRect = self.physicalRectF(cropRect, False).toRect()
        if realCropRect.size() != QSize(0, 0):
            cropPixmap = self.screenPixmap.copy(realCropRect)
            QApplication.clipboard().setPixmap(cropPixmap)
        self.clearScreenShot(False)
        self.close()

    def snip(self):
        if not self.hasScreenShot:
            return

        cropRect = self.normalizeRectF(self._pt_start, self._pt_end)
        realCropRect = self.physicalRectF(cropRect, False).toRect()
        if realCropRect.size() != QSize(0, 0):
            cropPixmap = self.screenPixmap.copy(realCropRect)
            screenPoint = self.mapToGlobal(cropRect.topLeft().toPoint())
            self.snipedSignal.emit(screenPoint, cropRect.size().toSize(), cropPixmap)
        self.clearScreenShot(False)
        self.close()

    def initPainterTool(self):
        self.painter = QPainter()
        self.color_transparent = Qt.GlobalColor.transparent
        self.color_black = QColor(0, 0, 0, 150)  # 黑色背景
        self.color_lightBlue = QColor(30, 120, 255, 255)  # 浅蓝色。深蓝色Qt.GlobalColor.blue
        self.color_lightWhite = QColor(255, 255, 255, 255)  # 浅蓝色。深蓝色Qt.GlobalColor.blue
        self.font_normal = QtGui.QFont('Times New Roman', 11, QtGui.QFont.Weight.Normal)
        self.font_textInput = QtGui.QFont('微软雅黑', 16, QtGui.QFont.Weight.Normal)  # 工具条文字工具默认字体
        self.pen_transparent = QPen(Qt.PenStyle.NoPen)  # 没有笔迹，画不出线条
        self.pen_white = QPen(Qt.GlobalColor.white)
        self.pen_SolidLine_lightBlue = QPen(self.color_lightBlue)  # 实线，浅蓝色
        self.pen_SolidLine_lightBlue.setStyle(Qt.PenStyle.SolidLine)  # 实线SolidLine，虚线DashLine，点线DotLine
        self.pen_SolidLine_lightBlue.setWidthF(4)  # 0表示线宽为1
        self.pen_SolidLine_lightWhite = QPen(self.color_lightWhite)  # 实线，浅蓝色
        self.pen_SolidLine_lightWhite.setStyle(Qt.PenStyle.SolidLine)  # 实线SolidLine，虚线DashLine，点线DotLine
        self.pen_SolidLine_lightWhite.setWidthF(2)  # 0表示线宽为1

    def clearScreenShot(self, isGotoScreeShot=True):
        self.hasScreenShot = False  # 是否已通过拖动鼠标左键划定截图区域
        self.isCapturing = False  # 正在拖动鼠标左键选定截图区域时
        self.isMoving = False  # 在截图区域内拖动时
        self.isAdjusting = False  # 在截图区域的边框按住鼠标左键调整大小时
        pos = QPointF()
        self.setCenterArea(pos, pos)
        self.update()
        if isGotoScreeShot:
            self.setCursor(Qt.CursorShape.CrossCursor)  # 设置鼠标样式 十字

    def expandScreenShotArea(self, pos):
        '''根据所处的非截图区域的朝向，拓展已划定的截取区域'''
        finalPolygon = QPolygonF(self.normalizeRectF(self._pt_start, self._pt_end))
        finalPolygon.append(pos)
        finalRect = finalPolygon.boundingRect()
        self.setCenterArea(finalRect.topLeft(), finalRect.bottomRight())
        self.update()

    def reShow(self):
        if self.isActiveWindow():
            return
        finalPixmap, finalGeometry = canvas_util.CanvasUtil.grabScreens()
        self.screenPixmap = finalPixmap
        self.setGeometry(finalGeometry)
        self.clearScreenShot()
        self.show()

    def normalizeRectF(self, topLeftPoint, bottomRightPoint):
        return QRectF(topLeftPoint, bottomRightPoint).normalized()

    def paintCenterArea(self):
        (rt_center, pt_centerTopMid, pt_centerBottomMid, pt_centerLeftMid, pt_centerRightMid) = self.getCenterInfos()

        # 绘制已选定的截图区域
        self.painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        # 1.绘制矩形线框
        self.painter.setPen(self.pen_SolidLine_lightBlue)
        self.painter.setBrush(self.color_transparent)
        self.painter.drawRect(rt_center)

        # 2.绘制矩形线框4个端点和4条边框的中间点
        if rt_center.width() >= 100 and rt_center.height() >= 100:
            # 选区操作点
            points = [
                rt_center.topLeft(), rt_center.topRight(), 
                rt_center.bottomLeft(), rt_center.bottomRight(),
                pt_centerLeftMid, pt_centerRightMid,
                pt_centerTopMid, pt_centerBottomMid,
            ]
            blueDotRadius = QPointF(5, 5)  # 椭圆蓝点
            self.painter.setPen(self.pen_SolidLine_lightWhite)
            self.painter.setBrush(self.color_lightBlue)
            for point in points:
                self.painter.drawEllipse(QRectF(point - blueDotRadius, point + blueDotRadius))

        # 显示截图区域宽高
        if rt_center.topLeft().y() > 20:
            labelPos = rt_center.topLeft() + QPointF(5, -5)
        else:
            labelPos = rt_center.topLeft() + QPointF(5, 15)
        self.painter.setPen(self.pen_white)
        self.painter.setFont(self.font_normal)
        physicalCenterRect = self.physicalRectF(rt_center).toRect()
        self.painter.drawText(labelPos, f"{physicalCenterRect.width()} x {physicalCenterRect.height()}")

    def setCenterArea(self, start, end):
        self._pt_start = start
        self._pt_end = end

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

    def setBeginDragPoint(self, pointf):
        '''计算开始拖拽位置距离截图区域左上角的向量'''
        rt_center = self.normalizeRectF(self._pt_start, self._pt_end)
        self._drag_vector = pointf - rt_center.topLeft()

    def getNewPosAfterDrag(self, pointf):
        '''计算拖拽后截图区域左上角的新位置'''
        return pointf - self._drag_vector

    def moveCenterAreaTo(self, pointf):
        '''限制拖拽不能超出屏幕范围'''
        rt_center = self.normalizeRectF(self._pt_start, self._pt_end)
        rt_center.moveTo(self.getNewPosAfterDrag(pointf))
        startPointF = rt_center.topLeft()
        if startPointF.x() < 0:
            rt_center.moveTo(0, startPointF.y())
            startPointF = rt_center.topLeft()
        if startPointF.y() < 0:
            rt_center.moveTo(startPointF.x(), 0)
        endPointF = rt_center.bottomRight()
        if endPointF.x() > self.rect().width():
            rt_center.moveBottomRight(QPointF(self.rect().width(), endPointF.y()))
            endPointF = rt_center.bottomRight()
        if endPointF.y() > self.rect().height():
            rt_center.moveBottomRight(QPointF(endPointF.x(), self.rect().height()))
        self.setCenterArea(rt_center.topLeft(), rt_center.bottomRight())

    def setBeginAdjustPoint(self, pointf):
        '''判断开始调整截图区域大小时鼠标左键在哪个区（不可能是中央区域），用于判断调整大小的意图方向'''
        self._mousePos = self.getMousePosBy(pointf, self._pt_start, self._pt_end)

    def getMousePosBy(self, pointf:QPointF, pt_start:QPointF, pt_end:QPointF):
        (rt_center, square_topLeft, square_topRight, square_bottomLeft, square_bottomRight, 
         square_topMid, square_bottomMid, square_leftMid, square_rightMid) = self.getSquareInfos()

        if square_topLeft.contains(pointf):
            return 'TL'
        elif square_topMid.contains(pointf):
            return 'T'
        elif square_topRight.contains(pointf):
            return 'TR'
        elif square_leftMid.contains(pointf):
            return 'L'
        elif square_rightMid.contains(pointf):
            return 'R'
        elif square_bottomLeft.contains(pointf):
            return 'BL'
        elif square_bottomMid.contains(pointf):
            return 'B'
        elif square_bottomRight.contains(pointf):
            return 'BR'
        elif rt_center.contains(pointf):
            return 'CENTER'
        else:
            return 'ERROR'

    def adjustCenterAreaBy(self, pointf):
        '''根据开始调整截图区域大小时鼠标左键在哪个区（不可能是中央区域），判断调整大小的意图方向，判定新的开始、结束位置'''
        rt_center = self.normalizeRectF(self._pt_start, self._pt_end)
        startPointF = rt_center.topLeft()
        endPointF = rt_center.bottomRight()
        if self._mousePos == 'TL':
            startPointF = pointf
        elif self._mousePos == 'T':
            startPointF.setY(pointf.y())
        elif self._mousePos == 'TR':
            startPointF.setY(pointf.y())
            endPointF.setX(pointf.x())
        elif self._mousePos == 'L':
            startPointF.setX(pointf.x())
        elif self._mousePos == 'R':
            endPointF.setX(pointf.x())
        elif self._mousePos == 'BL':
            startPointF.setX(pointf.x())
            endPointF.setY(pointf.y())
        elif self._mousePos == 'B':
            endPointF.setY(pointf.y())
        elif self._mousePos == 'BR':
            endPointF = pointf
        else:  # 'ERROR'
            return
        self.setCenterArea(startPointF, endPointF)

    def getCenterInfos(self):
        rt_center = self.normalizeRectF(self._pt_start, self._pt_end)
        # 中央区域上下左右边框的中点，用于调整大小
        pt_centerTopMid = (rt_center.topLeft() + rt_center.topRight()) / 2
        pt_centerBottomMid = (rt_center.bottomLeft() + rt_center.bottomRight()) / 2
        pt_centerLeftMid = (rt_center.topLeft() + rt_center.bottomLeft()) / 2
        pt_centerRightMid = (rt_center.topRight() + rt_center.bottomRight()) / 2
        return rt_center, pt_centerTopMid, pt_centerBottomMid, pt_centerLeftMid, pt_centerRightMid

    def getSquareInfos(self):
        rt_center, pt_centerTopMid, pt_centerBottomMid, pt_centerLeftMid, pt_centerRightMid = self.getCenterInfos()

        # 以截图区域左上、上中、右上、左中、右中、左下、下中、右下为中心的正方形区域，用于调整大小
        square_topLeft = self.squareAreaByCenter(rt_center.topLeft())
        square_topRight = self.squareAreaByCenter(rt_center.topRight())
        square_bottomLeft = self.squareAreaByCenter(rt_center.bottomLeft())
        square_bottomRight = self.squareAreaByCenter(rt_center.bottomRight())

        # 挪到四侧边缘操作检测区域，而不是采用边缘中心点的方式
        square_topMid = self.squareAreaByHorizontal(pt_centerTopMid, rt_center.width())
        square_bottomMid = self.squareAreaByHorizontal(pt_centerBottomMid, rt_center.width())
        square_leftMid = self.squareAreaByVertical(pt_centerLeftMid, rt_center.height())
        square_rightMid = self.squareAreaByVertical(pt_centerRightMid, rt_center.height())

        return rt_center, square_topLeft, square_topRight, square_bottomLeft, square_bottomRight, square_topMid, square_bottomMid, square_leftMid, square_rightMid


    def getMouseShapeBy(self, pointf):
        (rt_center, square_topLeft, square_topRight, square_bottomLeft, square_bottomRight, 
         square_topMid, square_bottomMid, square_leftMid, square_rightMid) = self.getSquareInfos()

        '''根据鼠标位置返回对应的鼠标样式'''
        if rt_center.contains(pointf):
            return Qt.CursorShape.SizeAllCursor  # 十字有箭头
        elif square_topLeft.contains(pointf) or square_bottomRight.contains(pointf):
            return Qt.CursorShape.SizeFDiagCursor  # ↖↘
        elif square_topMid.contains(pointf) or square_bottomMid.contains(pointf):
            return Qt.CursorShape.SizeVerCursor  # ↑↓
        elif square_topRight.contains(pointf) or square_bottomLeft.contains(pointf):
            return Qt.CursorShape.SizeBDiagCursor  # ↙↗
        elif square_leftMid.contains(pointf) or square_rightMid.contains(pointf):
            return Qt.CursorShape.SizeHorCursor  # ←→
        else:
            return Qt.CursorShape.CrossCursor  # 十字无箭头

    def isMousePosInCenterRectF(self, pointf):
        return self.normalizeRectF(self._pt_start, self._pt_end).contains(pointf)

    def paintMaskLayer(self, fullScreen=True):
        if fullScreen:  # 全屏遮罩层
            maskPixmap = QPixmap(self.rect().size())
            maskPixmap.fill(self.color_black)
            self.painter.drawPixmap(0, 0, maskPixmap)
        else:  # 绘制截图区域的周边区域遮罩层，以凸显截图区域
            cropRect = self.normalizeRectF(self._pt_start, self._pt_end).toRect()
            fullScreenRegion = QRegion(self.rect())
            cropRegion = QRegion(cropRect)
            finalRegion = fullScreenRegion.subtracted(cropRegion)
            finalPath = QPainterPath()
            finalPath.addRegion(finalRegion)
            self.painter.fillPath(finalPath, self.color_black)

    def paintEvent(self, event):
        canvasPixmap = self.screenPixmap.copy()
        self.painter.begin(canvasPixmap)

        if self.hasScreenShot:
            # 绘制截图区域的周边区域遮罩层
            self.paintMaskLayer(fullScreen=False)
            # 绘制中央截图区域
            self.paintCenterArea()
        else:
            self.paintMaskLayer()

        self.painter.end()

        self.painter.begin(self)
        self.painter.drawPixmap(0, 0, canvasPixmap)
        self.painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
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
        if event.button() == Qt.MouseButton.RightButton:
            self.cancelScreenShot()

    def cancelScreenShot(self):
        if self.hasScreenShot or self.isCapturing:  # 清空已划定的的截图区域
            self.clearScreenShot()
        else:
            self.close()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.isCapturing = False
            self.isMoving = False
            self.isAdjusting = False

    def mouseMoveEvent(self, event):
        pos = event.pos()
        if self.isVisible():
            self.mouse_pos:QPointF = pos
        if self.isCapturing:
            self.hasScreenShot = True
            self._pt_end = pos
        elif self.isMoving:
            self.moveCenterAreaTo(pos)
        elif self.isAdjusting:
            self.adjustCenterAreaBy(pos)
        self.update()
        if self.hasScreenShot:
            self.setCursor(self.getMouseShapeBy(pos))
        else:
            self.setCursor(Qt.CursorShape.CrossCursor)  # 设置鼠标样式 十字

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.isMousePosInCenterRectF(event.pos()):
                self.close()

    def physicalRectF(self, rectf:QRectF, isExpand = True):
        '''计算划定的截图区域的（缩放倍率1.0的）原始矩形（会变大）
        rectf：划定的截图区域的矩形。可为QRect或QRectF'''
        if isExpand:
            pixelRatio = self.screenPixmap.devicePixelRatio() + 0.0005
        else:
            pixelRatio = self.screenPixmap.devicePixelRatio()
        return QRectF(rectf.x() * pixelRatio, rectf.y() * pixelRatio,
                      rectf.width() * pixelRatio, rectf.height() * pixelRatio)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.closedSignal.emit()
        return super().closeEvent(a0)