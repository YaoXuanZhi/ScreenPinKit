# coding=utf-8
from canvas_item import *

class ScreenArea(QObject):
    '''屏幕区域（提供各种算法的核心类），划分为9个子区域：
    TopLeft，Top，TopRight
    Left，Center，Right
    BottomLeft，Bottom，BottomRight
    其中Center根据start、end两个QPointF确定
    '''

    Unknown = 0
    TopLeft = 1
    TopMid = 2
    TopRight = 3
    LeftMid = 4
    RightMid = 5
    BottomLeft = 6
    BottomMid = 7
    BottomRight = 8
    Center = 9

    def __init__(self, god):
        super().__init__()
        self.god = god
        self._pt_start = QPointF()  # 划定截图区域时鼠标左键按下的位置（topLeft）
        self._pt_end = QPointF()  # 划定截图区域时鼠标左键松开的位置（bottomRight）
        self._painter = QPainter()  # 独立于ScreenShotWidget之外的画家类
        self.captureScreen()

    def captureScreen(self):
        '''抓取整个屏幕的截图'''
        finalPixmap, finalGeometry = canvas_util.CanvasUtil.grabScreens()
        self._screenPixmap = finalPixmap
        # self._screenPixmap = QApplication.screenAt(QCursor.pos()).grabWindow(0)
        self._pixelRatio = self._screenPixmap.devicePixelRatio()  # 设备像素比
        self._rt_screen = self.screenLogicalRectF()
        self.remakeNightArea()

    def normalizeRectF(self, topLeftPoint, bottomRightPoint):
        return QRectF(topLeftPoint, bottomRightPoint).normalized()

    def physicalRectF(self, rectf):
        '''计算划定的截图区域的（缩放倍率1.0的）原始矩形（会变大）
        rectf：划定的截图区域的矩形。可为QRect或QRectF'''
        return QRectF(rectf.x() * self._pixelRatio, rectf.y() * self._pixelRatio,
                      rectf.width() * self._pixelRatio, rectf.height() * self._pixelRatio)

    def logicalRectF(self, physicalRectF):
        '''根据原始矩形计算缩放后的矩形（会变小）
        physicalRectF：缩放倍率1.0的原始矩形。可为QRect或QRectF'''
        return QRectF(physicalRectF.x() / self._pixelRatio, physicalRectF.y() / self._pixelRatio,
                      physicalRectF.width() / self._pixelRatio, physicalRectF.height() / self._pixelRatio)

    def physicalPixmap(self, rectf, editAction=False):
        '''根据指定区域获取其原始大小的（缩放倍率1.0的）QPixmap
        rectf：指定区域。可为QRect或QRectF
        editAction:是否带上编辑结果'''
        if editAction:
            canvasPixmap = self.screenPhysicalPixmapCopy()
            # self._painter.begin(canvasPixmap)
            # self.paintEachEditAction(self._painter, textBorder=False)
            # self._painter.end()
            return canvasPixmap.copy(self.physicalRectF(rectf).toRect())
        else:
            return self._screenPixmap.copy(self.physicalRectF(rectf).toRect())

    def screenPhysicalRectF(self):
        return QRectF(self._screenPixmap.rect())

    def screenLogicalRectF(self):
        return QRectF(QPointF(0, 0), self.screenLogicalSizeF())  # 即当前屏幕显示的大小

    def screenPhysicalSizeF(self):
        return QSizeF(self._screenPixmap.size())

    def screenLogicalSizeF(self):
        return QSizeF(self._screenPixmap.width() / self._pixelRatio, self._screenPixmap.height() / self._pixelRatio)

    def screenPhysicalPixmapCopy(self):
        return self._screenPixmap.copy()

    def screenLogicalPixmapCopy(self):
        return self._screenPixmap.scaled(self.screenLogicalSizeF().toSize())

    def centerPhysicalRectF(self):
        return self.physicalRectF(self._rt_center)

    def centerLogicalRectF(self):
        '''根据屏幕上的start、end两个QPointF确定'''
        return self._rt_center

    def centerPhysicalPixmap(self, editAction=True):
        '''截图区域的QPixmap
        editAction:是否带上编辑结果'''
        return self.physicalPixmap(self._rt_center + QMarginsF(-1, -1, 1, 1), editAction=editAction)

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
        self._rt_topLeft = QRectF(self._rt_screen.topLeft(), self._rt_center.topLeft())
        self._rt_top = QRectF(QPointF(self._rt_center.topLeft().x(), 0), self._rt_center.topRight())
        self._rt_topRight = QRectF(QPointF(self._rt_center.topRight().x(), 0), QPointF(self._rt_screen.width(), self._rt_center.topRight().y()))
        self._rt_left = QRectF(QPointF(0, self._rt_center.topLeft().y()), self._rt_center.bottomLeft())
        self._rt_right = QRectF(self._rt_center.topRight(), QPointF(self._rt_screen.width(), self._rt_center.bottomRight().y()))
        self._rt_bottomLeft = QRectF(QPointF(0, self._rt_center.bottomLeft().y()), QPointF(self._rt_center.bottomLeft().x(), self._rt_screen.height()))
        self._rt_bottom = QRectF(self._rt_center.bottomLeft(), QPointF(self._rt_center.bottomRight().x(), self._rt_screen.height()))
        self._rt_bottomRight = QRectF(self._rt_center.bottomRight(), self._rt_screen.bottomRight())

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
        screenSizeF = self.screenLogicalSizeF()
        pt_topRight = self._rt_center.topRight()
        pt_bottomLeft = self._rt_center.bottomLeft()
        return [QRectF(0, 0, screenSizeF.width(), pt_topRight.y()),
                QRectF(0, pt_bottomLeft.y(), screenSizeF.width(), screenSizeF.height() - pt_bottomLeft.y()),
                QRectF(0, 0, pt_bottomLeft.x(), screenSizeF.height()),
                QRectF(pt_topRight.x(), 0, screenSizeF.width() - pt_topRight.x(), screenSizeF.height())]

    def aroundAreaWithoutIntersection(self):
        '''中央区域周边的4个方向的区域（无交集）
        上区域(左上、上、右上)：0, 0, maxX, topRight.y
        下区域(左下、下、右下)：0, bottomLeft.y, maxX, maxY-bottomLeft.y
        左区域(左)：0, topRight.y, bottomLeft.x-1, center.height
        右区域(右)：topRight.x+1, topRight.y, maxX - topRight.x, center.height'''
        screenSizeF = self.screenLogicalSizeF()
        pt_topRight = self._rt_center.topRight()
        pt_bottomLeft = self._rt_center.bottomLeft()
        centerHeight = pt_bottomLeft.y() - pt_topRight.y()
        return [QRectF(0, 0, screenSizeF.width(), pt_topRight.y()),
                QRectF(0, pt_bottomLeft.y(), screenSizeF.width(), screenSizeF.height() - pt_bottomLeft.y()),
                QRectF(0, pt_topRight.y(), pt_bottomLeft.x() - 1, centerHeight),
                QRectF(pt_topRight.x() + 1, pt_topRight.y(), screenSizeF.width() - pt_topRight.x(), centerHeight)]

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
        screenSizeF = self.screenLogicalSizeF()
        endPointF = self._rt_center.bottomRight()
        if endPointF.x() > screenSizeF.width():
            self._rt_center.moveBottomRight(QPointF(screenSizeF.width(), endPointF.y()))
            endPointF = self._rt_center.bottomRight()
        if endPointF.y() > screenSizeF.height():
            self._rt_center.moveBottomRight(QPointF(endPointF.x(), screenSizeF.height()))
        self.setCenterArea(self._rt_center.topLeft(), self._rt_center.bottomRight())

    def setBeginAdjustPoint(self, pointf):
        '''判断开始调整截图区域大小时鼠标左键在哪个区（不可能是中央区域），用于判断调整大小的意图方向'''
        self._mousePos = self.getMousePosBy(pointf)

    def getMousePosBy(self, pointf):
        if self._square_topLeft.contains(pointf):
            return ScreenArea.TopLeft
        elif self._square_topMid.contains(pointf):
            return ScreenArea.TopMid
        elif self._square_topRight.contains(pointf):
            return ScreenArea.TopRight
        elif self._square_leftMid.contains(pointf):
            return ScreenArea.LeftMid
        elif self._square_rightMid.contains(pointf):
            return ScreenArea.RightMid
        elif self._square_bottomLeft.contains(pointf):
            return ScreenArea.BottomLeft
        elif self._square_bottomMid.contains(pointf):
            return ScreenArea.BottomMid
        elif self._square_bottomRight.contains(pointf):
            return ScreenArea.BottomRight
        elif self._rt_center.contains(pointf):
            return ScreenArea.Center
        else:
            return ScreenArea.Unknown

    # 获取拓展后的截图起始点和结束点
    def getExpandScreenShotArea(self, pointf):
        '''根据所处的非截图区域的朝向，拓展已划定的截取区域'''
        finalPolygon = QPolygonF(self.normalizeRectF(self._pt_start, self._pt_end))
        finalPolygon.append(pointf)
        finalRect = finalPolygon.boundingRect()
        return finalRect.topLeft(), finalRect.bottomRight()

    def adjustCenterAreaBy(self, pointf):
        '''根据开始调整截图区域大小时鼠标左键在哪个区（不可能是中央区域），判断调整大小的意图方向，判定新的开始、结束位置'''
        startPointF = self._rt_center.topLeft()
        endPointF = self._rt_center.bottomRight()
        if self._mousePos == ScreenArea.TopLeft:
            startPointF = pointf
        elif self._mousePos == ScreenArea.TopMid:
            startPointF = QPointF(startPointF.x(), pointf.y())
        elif self._mousePos == ScreenArea.TopRight:
            startPointF = QPointF(startPointF.x(), pointf.y())
            endPointF = QPointF(pointf.x(), endPointF.y())
        elif self._mousePos == ScreenArea.LeftMid:
            startPointF = QPointF(pointf.x(), startPointF.y())
        elif self._mousePos == ScreenArea.RightMid:
            endPointF = QPointF(pointf.x(), endPointF.y())
        elif self._mousePos == ScreenArea.BottomLeft:
            startPointF = QPointF(pointf.x(), startPointF.y())
            endPointF = QPointF(endPointF.x(), pointf.y())
        elif self._mousePos == ScreenArea.BottomMid:
            endPointF = QPointF(endPointF.x(), pointf.y())
        elif self._mousePos == ScreenArea.BottomRight:
            endPointF = pointf
        else:  # 'ScreenArea.Unknown'
            return
        newRectF = self.normalizeRectF(startPointF, endPointF)
        self.setCenterArea(newRectF.topLeft(), newRectF.bottomRight())

    def getMouseShapeBy(self, pointf):
        '''根据鼠标位置返回对应的鼠标样式'''
        if self._square_topLeft.contains(pointf) or self._square_bottomRight.contains(pointf):
            return Qt.CursorShape.SizeFDiagCursor  # ↖↘
        elif self._square_topMid.contains(pointf) or self._square_bottomMid.contains(pointf):
            return Qt.CursorShape.SizeVerCursor  # ↑↓
        elif self._square_topRight.contains(pointf) or self._square_bottomLeft.contains(pointf):
            return Qt.CursorShape.SizeBDiagCursor  # ↙↗
        elif self._square_leftMid.contains(pointf) or self._square_rightMid.contains(pointf):
            return Qt.CursorShape.SizeHorCursor  # ←→
        elif self._rt_center.contains(pointf):
            return Qt.CursorShape.SizeAllCursor
        else:
            return Qt.CursorShape.CrossCursor  # 十字无箭头

    def isMousePosInCenterRectF(self, pointf):
        return self._rt_center.contains(pointf)

    def paintMagnifyingGlassPixmap(self, pos, glassSize):
        '''绘制放大镜内的图像(含纵横十字线)
        pos:鼠标光标位置
        glassSize:放大镜边框大小'''
        pixmapRect = QRect(0, 0, 20, 20)  # 以鼠标光标为中心的正方形区域，最好是偶数
        pixmapRect.moveCenter(pos)
        glassPixmap = self.physicalPixmap(pixmapRect)
        glassPixmap.setDevicePixelRatio(1.0)
        glassPixmap = glassPixmap.scaled(glassSize, glassSize, Qt.AspectRatioMode.KeepAspectRatio)
        screenColor = glassPixmap.toImage().pixelColor(glassPixmap.rect().center())
        # 在放大后的QPixmap上画纵横十字线
        self._painter.begin(glassPixmap)
        halfWidth = glassPixmap.width() / 2
        halfHeight = glassPixmap.height() / 2
        self._painter.setPen(self.god.pen_SolidLine_lightBlue)
        self._painter.drawLine(QPointF(0, halfHeight), QPointF(glassPixmap.width(), halfHeight))
        self._painter.drawLine(QPointF(halfWidth, 0), QPointF(halfWidth, glassPixmap.height()))
        self._painter.end()
        return glassPixmap, screenColor

class ScreenShotWindow(QWidget):
    snipedSignal = pyqtSignal(QPoint, QSize, QPixmap)
    closedSignal = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.defaultFlag()

        self.initPainterTool()
        self.initFunctionalFlag()
        self.initActions()
        self.screenArea = ScreenArea(self)
        self.isUseHexColor = False
        # self.setWindowOpacity(0.5)

    def initActions(self):
        actions = [
            QAction(parent=self, triggered=self.copyToClipboard, shortcut="ctrl+c"),
            QAction(parent=self, triggered=self.snip, shortcut="ctrl+t"),
            QAction(parent=self, triggered=self.cancelScreenShot, shortcut="esc"),
            QAction(parent=self, triggered=self.pickUpScreenColor, shortcut="c"),
        ]
        self.addActions(actions)

    def defaultFlag(self):
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)

    def copyToClipboard(self):
        if not self.hasScreenShot:
            return

        if self.screenArea.centerLogicalRectF().toRect().size() != QSize(0, 0):
            cropPixmap = self.screenArea.centerPhysicalPixmap()
            QApplication.clipboard().setPixmap(cropPixmap)
        self.clearScreenShot(False)
        self.close()

    def snip(self):
        if not self.hasScreenShot:
            return

        cropRect = self.screenArea.centerLogicalRectF()
        if self.screenArea.centerLogicalRectF().toRect().size() != QSize(0, 0):
            cropPixmap = self.screenArea.centerPhysicalPixmap()
            screenPoint = self.mapToGlobal(cropRect.topLeft().toPoint())
            self.snipedSignal.emit(screenPoint, cropRect.size().toSize(), cropPixmap)
        self.clearScreenShot(False)
        self.close()

    def initFunctionalFlag(self):
        self.hasScreenShot = False  # 是否已通过拖动鼠标左键划定截图区域
        self.isCapturing = False  # 正在拖动鼠标左键选定截图区域时
        self.isMoving = False  # 在截图区域内拖动时
        self.isAdjusting = False  # 在截图区域的边框按住鼠标左键调整大小时
        self.setCursor(Qt.CursorShape.CrossCursor)  # 设置鼠标样式 十字

    def pickUpScreenColor(self):
        text = self.getScreenColorStr()
        QApplication.clipboard().setText(text)
        self.clearScreenShot(False)
        self.close()

    def cancelScreenShot(self):
        if self.hasScreenShot or self.isCapturing:  # 清空已划定的的截图区域
            self.clearScreenShotArea()
        else:
            self.close()

    def start(self):
        self.screenArea.captureScreen()
        self.setGeometry(self.screenArea.screenPhysicalRectF().toRect())
        self.clearScreenShotArea()

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
        self.pen_SolidLine_lightBlue.setWidthF(2)  # 0表示线宽为1
        self.pen_SolidLine_lightWhite = QPen(self.color_lightWhite)  # 实线，浅蓝色
        self.pen_SolidLine_lightWhite.setStyle(Qt.PenStyle.SolidLine)  # 实线SolidLine，虚线DashLine，点线DotLine
        self.pen_SolidLine_lightWhite.setWidthF(1.5)  # 0表示线宽为1

    def clearScreenShot(self, isGotoScreeShot=True):
        self.hasScreenShot = False  # 是否已通过拖动鼠标左键划定截图区域
        self.isCapturing = False  # 正在拖动鼠标左键选定截图区域时
        self.isMoving = False  # 在截图区域内拖动时
        self.isAdjusting = False  # 在截图区域的边框按住鼠标左键调整大小时
        pos = QPointF()
        self.screenArea.setCenterArea(pos, pos)
        self.update()
        if isGotoScreeShot:
            self.setCursor(Qt.CursorShape.CrossCursor)  # 设置鼠标样式 十字

    def reShow(self):
        if self.isActiveWindow():
            return
        self.start()
        self.show()
        self.activateWindow()

    def paintEvent(self, event):
        centerRectF = self.screenArea.centerLogicalRectF()
        screenSizeF = self.screenArea.screenLogicalSizeF()
        canvasPixmap = self.screenArea.screenPhysicalPixmapCopy()
        # 在屏幕截图的副本上绘制已选定的截图区域
        self.painter.begin(canvasPixmap)
        if self.hasScreenShot:
            self.paintCenterArea(centerRectF)  # 绘制中央截图区域
            self.paintMaskLayer(screenSizeF, fullScreen=False)  # 绘制截图区域的周边区域遮罩层
        else:
            self.paintMaskLayer(screenSizeF)
        self.paintMagnifyingGlass(screenSizeF)  # 在鼠标光标右下角显示放大镜
        self.painter.end()
        # 把画好的绘制结果显示到窗口上
        self.painter.begin(self)
        self.painter.drawPixmap(0, 0, canvasPixmap)  # 从坐标(0, 0)开始绘制
        self.painter.end()

    def paintCenterArea(self, centerRectF:QRectF):
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
                self.screenArea.centerLeftMid(), self.screenArea.centerRightMid(),
                self.screenArea.centerTopMid(), self.screenArea.centerBottomMid()
            ]
            blueDotRadius = QPointF(5, 5)  # 椭圆蓝点
            self.painter.setPen(self.pen_SolidLine_lightWhite)
            self.painter.setBrush(self.color_lightBlue)
            for point in points:
                self.painter.drawEllipse(QRectF(point - blueDotRadius, point + blueDotRadius))

        # 3.在截图区域左上角显示截图区域宽高
        if centerRectF.topLeft().y() > 20:
            labelPos = centerRectF.topLeft() + QPointF(5, -5)
        else:  # 拖拽截图区域到贴近屏幕上边缘时“宽x高”移动到截图区域左上角的下侧
            labelPos = centerRectF.topLeft() + QPointF(5, 15)
        centerPhysicalRect = self.screenArea.centerPhysicalRectF().toRect()
        self.painter.setPen(self.pen_white)
        self.painter.setFont(self.font_normal)
        self.painter.drawText(labelPos, '%s x %s' % (centerPhysicalRect.width(), centerPhysicalRect.height()))

    def paintMaskLayer(self, screenSizeF:QSizeF, fullScreen=True):
        if fullScreen:  # 全屏遮罩层
            maskPixmap = QPixmap(screenSizeF.toSize())
            maskPixmap.fill(self.color_black)
            self.painter.drawPixmap(0, 0, maskPixmap)
        else:  # 绘制截图区域的周边区域遮罩层，以凸显截图区域
            for area in self.screenArea.aroundAreaWithoutIntersection():
                maskPixmap = QPixmap(area.size().toSize())
                maskPixmap.fill(self.color_black)
                self.painter.drawPixmap(area.topLeft(), maskPixmap)

    def paintMagnifyingGlass(self, screenSizeF:QSizeF, glassSize=150, offset=30, labelHeight=60):
        '''未划定截图区域模式时、正在划定截取区域时、调整截取区域大小时在鼠标光标右下角显示放大镜
        glassSize:放大镜正方形边长
        offset:放大镜任意一个端点距离鼠标光标位置的最近距离
        labelHeight:pos和rgb两行文字的高度'''
        if self.hasScreenShot and (not self.isCapturing) and (not self.isAdjusting):
            return
        pos = QtGui.QCursor.pos()
        glassPixmap, screenColor = self.screenArea.paintMagnifyingGlassPixmap(pos, glassSize)  # 画好纵横十字线后的放大镜内QPixmap
        self.screenColor = screenColor
        # 限制放大镜显示不超出屏幕外
        glassRect = glassPixmap.rect()
        if (pos.x() + glassSize + offset) < screenSizeF.width():
            if (pos.y() + offset + glassSize + labelHeight) < screenSizeF.height():
                glassRect.moveTo(pos + QPoint(offset, offset))
            else:
                glassRect.moveBottomLeft(pos + QPoint(offset, -offset))
        else:
            if (pos.y() + offset + glassSize + labelHeight) < screenSizeF.height():
                glassRect.moveTopRight(pos + QPoint(-offset, offset))
            else:
                glassRect.moveBottomRight(pos + QPoint(-offset, -offset))
        self.painter.drawPixmap(glassRect.topLeft(), glassPixmap)
        self.painter.setPen(QPen(Qt.GlobalColor.white, 2, Qt.SolidLine))
        self.painter.drawRect(glassRect - QMargins(2, 2, 2, 2))
        tempRect = QRectF(QPointF(0, 0), pos)
        physicalPoint = self.screenArea.physicalRectF(tempRect).toRect().bottomRight()
        labelRectF = QRectF(glassRect.bottomLeft().x(), glassRect.bottomLeft().y(), glassSize, labelHeight)
        self.painter.setPen(self.pen_transparent)
        self.painter.fillRect(labelRectF, self.color_black)
        self.painter.setPen(self.pen_white)
        self.painter.setFont(self.font_normal)
        labelRectF = labelRectF - QMarginsF(12, 10, 12, 10)
        self.painter.drawText(labelRectF,
                              Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                              f"({physicalPoint.x()}, {physicalPoint.y()})")

        self.painter.drawText(labelRectF,
                            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom,
                            self.getScreenColorStr())

        self.painter.setBrush(Qt.NoBrush)
        self.painter.setPen(QPen(screenColor, 3))
        self.painter.drawRect(labelRectF)

    def getScreenColorStr(self):
        if self.isUseHexColor:
            return f"hex:{self.screenColor.name()}"
        else:
            return f"rgb:({self.screenColor.red()}, {self.screenColor.green()}, {self.screenColor.blue()})"

    def clearScreenShotArea(self):
        '''清空已划定的截取区域'''
        self.hasScreenShot = False
        self.isCapturing = False
        pos = QPointF()
        self.screenArea.setCenterArea(pos, pos)
        self.update()
        self.setCursor(Qt.CursorShape.CrossCursor)  # 设置鼠标样式 十字

    def expandScreenShotArea(self, pos):
        '''根据所处的非截图区域的朝向，拓展已划定的截取区域'''
        pt_start, pt_end = self.screenArea.getExpandScreenShotArea(pos)
        self.screenArea.setCenterArea(pt_start, pt_end)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            if self.hasScreenShot:
                if self.screenArea.isMousePosInCenterRectF(pos):
                    self.isMoving = True  # 进入拖拽移动模式
                    self.screenArea.setBeginDragPoint(pos)
                else:
                    self.isAdjusting = True  # 进入调整大小模式
                    self.screenArea.setBeginAdjustPoint(pos)

                    # 如果在非截图区进行点击，那么直接拓展截图区
                    if self.screenArea._mousePos == ScreenArea.Unknown:
                        self.expandScreenShotArea(pos)
            else:
                self.screenArea.setCenterArea(pos, pos)
                self.isCapturing = True  # 进入划定截图区域模式
        if event.button() == Qt.MouseButton.RightButton:
            if self.hasScreenShot or self.isCapturing:  # 清空已划定的的截图区域
                self.clearScreenShotArea()
            else:
                self.close()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.isCapturing = False
            self.isMoving = False
            self.isAdjusting = False

    def mouseMoveEvent(self, event):
        pos = event.pos()
        if self.isCapturing:
            self.hasScreenShot = True
            self.screenArea.setEndPoint(pos, remake=True)
        elif self.isMoving:
            self.screenArea.moveCenterAreaTo(pos)
        elif self.isAdjusting:
            self.screenArea.adjustCenterAreaBy(pos)
        self.update()
        if self.hasScreenShot:
            self.setCursor(self.screenArea.getMouseShapeBy(pos))
        else:
            self.setCursor(Qt.CursorShape.CrossCursor)  # 设置鼠标样式 十字


    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.screenArea.isMousePosInCenterRectF(event.pos()):
                self.close()

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.closedSignal.emit()
        return super().closeEvent(a0)

    def keyPressEvent(self, event: QKeyEvent):
        if int(event.modifiers()) == Qt.Modifier.SHIFT:
            self.isUseHexColor = not self.isUseHexColor
            self.update()
        super().keyPressEvent(event)