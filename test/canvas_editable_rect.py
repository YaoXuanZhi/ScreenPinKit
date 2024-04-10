# https://blog.csdn.net/qq_33659478/article/details/126646020
# https://blog.csdn.net/xiaonuo911teamo/article/details/106129696
# https://blog.csdn.net/xiaonuo911teamo/article/details/106075647
import math
from enum import Enum
from collections import OrderedDict, deque
from PyQt5 import QtCore
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsSceneDragDropEvent, QGraphicsSceneHoverEvent, QGraphicsSceneMouseEvent, QStyleOptionGraphicsItem, QWidget
import win32api, win32con, win32gui, ctypes, win32ui
from PyQt5.QtWinExtras import QtWin
from PyQt5.QtSvg import QSvgWidget, QSvgRenderer
from canvas_util import CanvasUtil

class EnumPosType(Enum):
    ControllerPosTL = "左上角"
    ControllerPosTC = "顶部居中"
    ControllerPosTR = "右上角"
    ControllerPosRC = "右侧居中"
    ControllerPosBR = "右下角"
    ControllerPosBC = "底部居中"
    ControllerPosBL = "左下角"
    ControllerPosLC = "左侧居中"
    ControllerPosTT = "顶部悬浮"

class CanvasBaseItem(QGraphicsObject):
    def __init__(self, parent: QGraphicsItem) -> None:
        super().__init__(parent)

        self.m_pen = QPen(Qt.yellow)
        self.m_brush = QBrush(Qt.red)

        self.m_rect = QRectF()
        self.m_boundingRect = QRectF()

    def setPen(self, pen:QPen):
        if self.m_pen == pen:
            return
        self.prepareGeometryChange()
        self.m_pen = pen
        self.m_boundingRect = QRectF()
        self.update()

    def setBrush(self, brush:QBrush):
        if self.m_brush == brush:
            return
        self.m_brush = brush
        self.update()

    def setBrush(self, brush:QBrush):
        self.m_brush = brush

    def rect(self) -> QRectF:
        return self.m_rect

    def setRect(self, rect:QRectF):
        if self.m_rect == rect:
            return

        self.prepareGeometryChange()
        self.m_rect = rect
        self.m_boundingRect = QRectF()
        self.update()

    def boundingRect(self) -> QRectF:
        if(self.m_boundingRect.isNull()):
            self.m_boundingRect = self.m_rect
        return self.m_boundingRect

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        if self.m_rect.isNull():
            return path
        path.addEllipse(self.m_rect)
        return path

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        painter.save()

        painter.setPen(self.m_pen)
        painter.setBrush(self.m_brush)

        painter.drawEllipse(self.m_rect)

        painter.restore()

class CanvasEllipseItem(CanvasBaseItem):
    def __init__(self, interfaceCursor:QCursor, parent:QGraphicsItem = None) -> None:
        super().__init__(parent)
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)
        self.lastCursor = None
        self.interfaceCursor = interfaceCursor

        pen = QPen()
        pen.setColor(Qt.lightGray)
        pen.setWidth(1)
        self.setPen(pen)
        self.setBrush(QBrush(Qt.NoBrush))
        # self.setBrush(Qt.blue)

    def getMouseCursorIconWinNew(self) -> QPixmap:
        cursorInfo = win32gui.GetCursorInfo()
        pixmap = QtWin.fromHICON(cursorInfo[1])
        return pixmap

    def getMouseCursorIconWin(self) -> QPixmap:
    #   cursorWidth = ctypes.windll.user32.GetSystemMetrics(win32con.SM_CXCURSOR), 
    #   cursorHeight = ctypes.windll.user32.GetSystemMetrics(win32con.SM_CYCURSOR)

        ci = win32gui.GetCursorInfo() #获取光标信息

        print(f'包含光标类型，句柄，坐标 {ci}') #包含光标类型，句柄，坐标
        print(f'GetCursor获取的句柄 {win32gui.GetCursor()}')#win32gui.GetCursor()也为获取光标句柄 但和GetCursorInfo获取的句柄并不相同，不清楚为什么?

        if(ci [1]==0):#在某些时候光标会被游戏或程序隐藏，因此报错
            print("光标消失")

        #-----------------------------------------------作废
        #e=win32gui.SetCursor(ci[1])#更改光标 返回旧光标句柄类型
        #print type(e)
        #if (e == 0):
            #print "光标消失"
            #continue
        #---------------------------------------------作废
        ii=win32gui.GetIconInfo(ci[1])#返回光标的图像信息，注意：参数不可为win32gui.GetCursor()得到的句柄，不然热点读取出错，why？
        print(f'光标参数 {ii}') #光标类型，热点坐标x，y，黑白位图，彩色位图
        #我想用彩色位图导出bmp图片并不成功，在c++将位图放入Cimg.Attach里很轻松就能save搞定
        #然后我并不清楚python内是否有可以使用的方法，pil里面是没找到
        bm = win32gui.GetObject(ii[3])#返回PyBITMAP类型 可以获得光标尺寸，注意，这里最好放入黑白位图来获取，放入彩色位图可能导致单色光标报错
        print(f"高 {bm.bmHeight} 宽 {bm.bmWidth}")

        gdc=win32gui.GetDC(0)#使指定上下文0中提取出一个句柄，记得释放 0也应该表示整个屏幕
        hdc = win32ui.CreateDCFromHandle(gdc)#依据其句柄创造出一个DC对象
        hbmp = win32ui.CreateBitmap()#创建一个新位图
        hbmp.CreateCompatibleBitmap(hdc,bm.bmWidth, bm.bmHeight)#设置位图 使其与上下文兼容以及图片的大小
        hdc = hdc.CreateCompatibleDC()#建立一个与屏幕兼容的DC
        # CreateCompatibleDC相当于在内存开辟一块地方，将屏幕或窗口复制进来，再对其操作，待操作完成后
        #再复制回屏幕，完成对屏幕的刷新
        hdc.SelectObject(hbmp)#将位图放入上下文中，就可以对位图进行编辑了

        win32gui.DrawIconEx(hdc.GetHandleOutput(), 0, 0, ci[1], bm.bmWidth, bm.bmHeight, 0, None,2)#图标大小
        #DrawIconEx 绘制位图放入到指定的上下文中
        #hdc.GetHandleOutput()返回上下文句柄
        #参数（需要放入的上下文句柄，x坐标，y坐标，需要放入的光标句柄，光标的高，光标的宽，动画光标取第几帧，背景画笔（可以是空），绘图类型int）
        bitmapbits = hbmp.GetBitmapBits(True)#将该图片转换为字符串

        # cursorPixmap = QtWin.fromHBITMAP(hbmp, QtWin.HBitmapFormat.HBitmapAlpha)
        # cursorPixmap = QtWin.fromHBITMAP(bitmapbits)
        cursorPixmap = QPixmap()
        # cursorPixmap.loadFromData(bitmapbits)

        # print(f"{bitmapbits}")
        hbmp.SaveBitmapFile(hdc, 'scre99t.bmp')#将位图保存为图片，注意这里只能放dc

        print(f"========> {hbmp.GetInfo()}")
        bmp = QBitmap()
        # bmp.fromData(len(bitmapbits), bitmapbits, QImage.Format.Format_ARGB32)
        bmp.fromData(QSize(hbmp.GetSize()[0], hbmp.GetSize()[1]), bitmapbits, QImage.Format.Format_ARGB32)
        bmp.save("fffff.bmp")

        #资源释放
        win32gui.ReleaseDC(0, gdc)#释放上下文 参数（窗口句柄，上下文句柄）
        hdc.DeleteDC()
        win32gui.DeleteObject(hbmp.GetHandle())
        return cursorPixmap

    def setSystemCursor(self, hoverCursor) -> QCursor:
        # parentItem:CanvasEditableFrame = self.parentItem()
        parentItem = self.parentItem()
        self.setCursor(self.interfaceCursor)
        # if self.posType == EnumPosType.ControllerPosTT:
        #     self.setCursor(self.interfaceCursor)
        #     return

        pixmap = self.getMouseCursorIconWin()
        # pixmap = self.getMouseCursorIconWinNew()
        transform = parentItem.transform()
        transform.rotate(parentItem.rotation())
        finalPixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
        newFinal = QCursor(finalPixmap, -1, -1)
        self.setCursor(newFinal)
        return

        # 加载移动箭头光标资源
        # hCursor = win32api.LoadCursor(0, win32con.IDC_SIZEALL)
        hCursor = win32api.LoadCursor(0, win32con.IDC_SIZENS)
        # width = int(ctypes.windll.user32.GetSystemMetrics(win32con.SM_CXCURSOR)),
        # height = int(ctypes.windll.user32.GetSystemMetrics(win32con.SM_CYCURSOR))
        width = 48
        height = 48

        print(f"=====> {width} : {height}")

        # cursorInfo = win32gui.GetCursorInfo()
        # # hCursor = cursorInfo[1]
        # hCursor = win32gui.GetCursor()
        # iconInfo = win32gui.GetIconInfo(hCursor)

        # bm = win32gui.GetObject(iconInfo[3])
        # width = bm.bmWidth
        # height = bm.bmHeight

        # 将光标资源转换为QPixmap对象
        icon = QIcon(QtWin.fromHICON(hCursor))
        # pixmap = QPixmap.fromImage(icon.pixmap(48, 48).toImage())
        pixmap:QPixmap = icon.pixmap(width, height)
        # pixmap.save("tsete.png")

        transform = parentItem.transform()
        transform.rotate(parentItem.rotation())
        finalPixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
        newFinal = QCursor(finalPixmap, -1, -1)
        self.setCursor(newFinal)

    def setCustomCursor(self) -> QCursor:
        # parentItem:CanvasEditableFrame = self.parentItem()
        parentItem = self.parentItem()
        if self.posType == EnumPosType.ControllerPosTT:
            self.setCursor(self.interfaceCursor)
            return
        elif self.posType == EnumPosType.ControllerPosRC:
            pixmap = QPixmap("images/horizontal resize.png")
        elif self.posType == EnumPosType.ControllerPosLC:
            pixmap = QPixmap("images/horizontal resize.png")
        elif self.posType == EnumPosType.ControllerPosTC:
            pixmap = QPixmap("images/vertical resize.png")
        elif self.posType == EnumPosType.ControllerPosBC:
            pixmap = QPixmap("images/vertical resize.png")
        elif self.posType == EnumPosType.ControllerPosTL:
            pixmap = QPixmap("images/diagonal resize 1.png")
        elif self.posType == EnumPosType.ControllerPosBR:
            pixmap = QPixmap("images/diagonal resize 1.png")
        elif self.posType == EnumPosType.ControllerPosTR:
            pixmap = QPixmap("images/diagonal resize 2.png")
        elif self.posType == EnumPosType.ControllerPosBL:
            pixmap = QPixmap("images/diagonal resize 2.png")
        else:
            pixmap = QPixmap("images/location select.png")

        pixmap = pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        transform = parentItem.transform()
        transform.rotate(parentItem.rotation())
        finalPixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
        newFinal = QCursor(finalPixmap, -1, -1)
        self.setCursor(newFinal)

    def setSvgCursor(self) -> QCursor:
        # parentItem:CanvasEditableFrame = self.parentItem()
        parentItem = self.parentItem()
        if self.posType == EnumPosType.ControllerPosTT:
            self.setCursor(self.interfaceCursor)
            return
        else:
            svgRender = QSvgRenderer("../test/resources/diagonal resize 2.svg")
            pixmap = QPixmap(128, 128)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter()
            painter.begin(pixmap)
            svgRender.render(painter)
            painter.end()

        pixmap = pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        transform = parentItem.transform()
        transform.rotate(parentItem.rotation())
        finalPixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
        newFinal = QCursor(finalPixmap, -1, -1)
        self.setCursor(newFinal)
   
    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.lastCursor = self.cursor()
        self.setCursor(self.interfaceCursor)
        # self.setSystemCursor(self.interfaceCursor)
        # self.setCustomCursor()
        # self.setSvgCursor()

        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        if self.lastCursor != None:
            self.setCursor(self.lastCursor)
            self.lastCursor = None
        return super().hoverLeaveEvent(event)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        if self.isSelected():
            option.state = QStyle.StateFlag.State_None
        return super().paint(painter, option, widget)

    def getControllerPosition(self, rect:QRectF, radius, posType:EnumPosType):
        if posType == EnumPosType.ControllerPosTL:
            # 左上角
            return rect.topLeft() - QPointF(radius, radius)
        elif posType == EnumPosType.ControllerPosTC:
            # 顶端居中
            return (rect.topLeft() + rect.topRight()) / 2 - QPointF(radius, radius)
        elif posType == EnumPosType.ControllerPosTR:
            # 右上角
            return rect.topRight() - QPointF(radius, radius)
        elif posType == EnumPosType.ControllerPosRC:
            # 右侧居中
            return (rect.topRight() + rect.bottomRight()) / 2 - QPointF(radius, radius)
        elif posType == EnumPosType.ControllerPosBL:
            # 左下角
            return rect.bottomLeft() - QPointF(radius, radius)
        elif posType == EnumPosType.ControllerPosBC:
            # 底端居中
            return (rect.bottomLeft() + rect.bottomRight()) / 2 - QPointF(radius, radius)
        elif posType == EnumPosType.ControllerPosBR:
            # 右下角
            return rect.bottomRight() - QPointF(radius, radius)
        elif posType == EnumPosType.ControllerPosLC:
            # 左侧居中
            return (rect.topLeft() + rect.bottomLeft()) / 2 - QPointF(radius, radius)
        elif posType == EnumPosType.ControllerPosTT:
            # 顶部悬浮
            hoverDistance = 30
            return (rect.topLeft() + rect.topRight()) / 2 - QPointF(radius, radius + hoverDistance)

    def setRectWrapper(self, attachRect:QRectF, posType:EnumPosType, radius:float, size:QSizeF):
        self.posType = posType
        pos = self.getControllerPosition(attachRect, radius, posType)
        self.setRect(QRectF(pos, size))

    def resetPosition(self, attachRect:QRectF, radius:float, size:QSizeF):
        pos = self.getControllerPosition(attachRect, radius, self.posType)
        self.setRect(QRectF(pos, size))

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        # parentItem:CanvasEditableFrame = self.parentItem()
        parentItem = self.parentItem()
        if self.posType == EnumPosType.ControllerPosTT:
            parentItem.mouseMoveRotateOperator(event.scenePos(), event.pos())
            return
        parentItem.updateEdge(self.posType, event.pos().toPoint())

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        # parentItem:CanvasEditableFrame = self.parentItem()
        parentItem = self.parentItem()
        if self.posType == EnumPosType.ControllerPosTT:
            parentItem.startRotate(event.pos())
        else:
            parentItem.startResize(event.pos())
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        # parentItem:CanvasEditableFrame = self.parentItem()
        parentItem = self.parentItem()
        if self.posType == EnumPosType.ControllerPosTT:
            parentItem.endRotate(event.pos())
        else:
            parentItem.endResize(event.pos())
        return super().mouseReleaseEvent(event)

# class CanvasEditableFrame(QGraphicsRectItem):
#     def __init__(self, rect: QRectF, parent:QGraphicsItem = None) -> None:
#         super().__init__(rect, parent)

#         self.radius = 8
#         self.m_borderWidth = 1

#         self.m_penDefault = QPen(Qt.white, self.m_borderWidth)
#         self.m_penSelected = QPen(QColor("#FFFFA637"), self.m_borderWidth)

#         self.initUI()

#     def initUI(self):
#         self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
#         self.setAcceptHoverEvents(True)

#         self.lastCursor = None
#         self.shapePath = QPainterPath()

#         self.m_pressPos = QPointF() # 本地坐标点击的点

#     def initControllers(self):
#         if not hasattr(self, "controllers"):
#             self.controllers:list[CanvasEllipseItem] = []

#         rect = self.boundingRect()
#         size = QSizeF(self.radius*2, self.radius*2)
#         posTypes = [
#             [EnumPosType.ControllerPosTL, Qt.CursorShape.SizeFDiagCursor], 
#             [EnumPosType.ControllerPosTC, Qt.CursorShape.SizeVerCursor], 
#             [EnumPosType.ControllerPosTR, Qt.CursorShape.SizeBDiagCursor], 
#             [EnumPosType.ControllerPosRC, Qt.CursorShape.SizeHorCursor], 
#             [EnumPosType.ControllerPosBR, Qt.CursorShape.SizeFDiagCursor], 
#             [EnumPosType.ControllerPosBC, Qt.CursorShape.SizeVerCursor], 
#             [EnumPosType.ControllerPosBL, Qt.CursorShape.SizeBDiagCursor], 
#             [EnumPosType.ControllerPosLC, Qt.CursorShape.SizeHorCursor],
#             [EnumPosType.ControllerPosTT, Qt.CursorShape.PointingHandCursor],
#             ]

#         if len(self.controllers) == 0:
#             for info in posTypes:
#                 controller = CanvasEllipseItem(info[-1], self)
#                 controller.setRectWrapper(rect, info[0], self.radius, size)
#                 self.controllers.append(controller)
#         else:
#             for controller in self.controllers:
#                 controller.resetPosition(rect, self.radius, size)
#                 if not controller.isVisible():
#                     controller.show()

#     def hideControllers(self):
#         if not hasattr(self, "controllers"):
#             return
#         for controller in self.controllers:
#             if controller.isVisible():
#                 controller.hide()

#     def mouseMoveRotateOperator(self, scenePos:QPointF, localPos:QPointF) -> None:
#         p1 = QLineF(self.originPos, self.m_pressPos)
#         p2 = QLineF(self.originPos, localPos)

#         dRotateAngle = p2.angleTo(p1)

#         dCurAngle = self.rotation() + dRotateAngle
#         while dCurAngle > 360.0:
#             dCurAngle -= 360.0
#         self.setRotation(dCurAngle)
#         self.update()

#     def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
#         self.lastCursor = self.cursor()
#         self.setCursor(Qt.CursorShape.SizeAllCursor)
#         return super().hoverEnterEvent(event)

#     def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
#         if self.lastCursor != None:
#             self.setCursor(self.lastCursor)
#             self.lastCursor = None
#         return super().hoverLeaveEvent(event)

#     def updateEdge(self, currentPosType, localPos:QPoint):
#         offset = self.m_borderWidth / 2
#         lastRect = self.rect()
#         newRect = lastRect.adjusted(0, 0, 0, 0)
#         if currentPosType == EnumPosType.ControllerPosTL:
#             localPos += QPoint(-offset, -offset)
#             newRect.setTopLeft(localPos)
#         elif currentPosType == EnumPosType.ControllerPosTC:
#             localPos += QPoint(0, -offset)
#             newRect.setTop(localPos.y())
#         elif currentPosType == EnumPosType.ControllerPosTR:
#             localPos += QPoint(offset, -offset)
#             newRect.setTopRight(localPos)
#         elif currentPosType == EnumPosType.ControllerPosRC:
#             localPos += QPoint(offset, 0)
#             newRect.setRight(localPos.x())
#         elif currentPosType == EnumPosType.ControllerPosBR:
#             localPos += QPoint(offset, offset)
#             newRect.setBottomRight(localPos)
#         elif currentPosType == EnumPosType.ControllerPosBC:
#             localPos += QPoint(0, offset)
#             newRect.setBottom(localPos.y())
#         elif currentPosType == EnumPosType.ControllerPosBL:
#             localPos += QPoint(-offset, offset)
#             newRect.setBottomLeft(localPos)
#         elif currentPosType == EnumPosType.ControllerPosLC:
#             localPos = localPos - QPoint(offset, offset)
#             newRect.setLeft(localPos.x())

#         self.setRect(newRect)

#     def hasFocusWrapper(self):
#         # if self.hasFocus() or self.isSelected():
#         if self.hasFocus():
#             return True
#         else:
#             if hasattr(self, 'controllers'):
#                 for controller in self.controllers:
#                     if controller.hasFocus():
#                         return True
#         return False

#     # 修改光标选中的区域 https://doc.qt.io/qtforpython-5/PySide2/QtGui/QRegion.html
#     def shape(self) -> QPainterPath:
#         self.shapePath.clear()
#         if self.hasFocusWrapper():
#             region = QRegion()
#             rects = [self.boundingRect().toRect()]
#             if hasattr(self, 'controllers'):
#                 for controller in self.controllers:
#                     rects.append(controller.boundingRect().toRect())
#             region.setRects(rects)
#             self.shapePath.addRegion(region)
#         else:
#             fullRect = self.boundingRect()
#             selectRegion = QRegion(fullRect.toRect())
#             offset = self.m_borderWidth
#             subRect:QRectF = self.boundingRect() - QMarginsF(offset, offset, offset, offset)
#             finalRegion = selectRegion.subtracted(QRegion(subRect.toRect()))
#             self.shapePath.addRegion(finalRegion)
#         return self.shapePath

#     def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
#         painter.save()

#         boundingRect = self.rect()
#         boundingColor = QColor(0, 0, 125)

#         # painter.setPen(boundingColor)
#         painter.setPen(self.m_penDefault if not self.hasFocusWrapper() else self.m_penSelected)
#         painter.drawRect(boundingRect)
#         painter.setPen(Qt.white)

#         painter.restore()

#         if self.hasFocusWrapper():
#             self.initControllers()
#         else:
#             self.hideControllers()

#     def startResize(self, localPos:QPointF) -> None:
#         pass

#     def endResize(self, localPos:QPointF) -> None:
#         # 解决有旋转角度的矩形，拉伸之后，再次旋转，旋转中心该仍然为之前坐标，手动设置为中心，会产生漂移的问题
#         rect = self.rect()
#         angle = math.radians(self.rotation())

#         p1 = rect.center()
#         origin = self.transformOriginPoint()
#         p2 = QPointF(0, 0)

#         p2.setX(origin.x() + math.cos(angle)*(p1.x() - origin.x()) - math.sin(angle)*(p1.y() - origin.y()))
#         p2.setY(origin.y() + math.sin(angle)*(p1.x() - origin.x()) + math.cos(angle)*(p1.y() - origin.y()))

#         diff:QPointF = p1 - p2

#         self.setRect(rect.adjusted(-diff.x(), -diff.y(), -diff.x(), -diff.y()))
#         self.setTransformOriginPoint(p1-diff)

#         self.initControllers()

#     def startRotate(self, localPos:QPointF) -> None:
#         self.originPos = self.boundingRect().center()
#         self.setTransformOriginPoint(self.originPos)
#         self.m_pressPos = localPos
    
#     def endRotate(self, localPos:QPointF) -> None:
#         pass

# class CanvasROI(CanvasBaseItem):
class CanvasROI(QGraphicsEllipseItem):
    def __init__(self, hoverCursor:QCursor, id:int, parent:QGraphicsItem = None) -> None:
        super().__init__(parent)
        self.hoverCursor = hoverCursor
        self.id = id
        self.initUI()

    def initUI(self):
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)
        self.lastCursorDeque = deque()
        self.isMoving = False

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.isMoving = True
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.isMoving = False
        # parentItem:CanvasEditableFrame = self.parentItem()
        parentItem = self.parentItem()
        parentItem.endResize(event.pos())
        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseMoveEvent(event)
        if self.isMoving:
            parentItem:CanvasEditablePath = self.parentItem()
            localPos = self.mapToItem(parentItem, self.rect().center())
            parentItem.movePointById(self, localPos)

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.lastCursor = self.cursor()
        self.setCursor(self.hoverCursor)
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        if self.lastCursor != None:
            self.setCursor(self.lastCursor)
            self.lastCursor = None
        return super().hoverLeaveEvent(event)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            parentItem:CanvasEditablePath = self.parentItem()
            parentItem.removePoint(self)
        return super().mouseDoubleClickEvent(event)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        super().paint(painter, option, widget)
        parentItem:CanvasEditablePath = self.parentItem()

        painter.save()
        painter.setPen(Qt.white)
        font = painter.font()
        font.setPixelSize(12)
        painter.setFont(font)
        index = parentItem.roiItemList.index(self)
        painter.drawText(self.rect(), Qt.AlignCenter, f"{index}/{self.id}")
        painter.restore()

class CanvasEditablePath(QGraphicsObject):
    RoiEditableMode = 1 << 0 # Roi点可编辑模式
    FrameEditableMode = 1 << 1 # 边框可编辑模式
    FocusFrameMode = 1 << 2 # 焦点框模式
    AdvanceSelectMode = 1 << 3 # 高级选择模式

    def setEditMode(self, flag, isEnable:bool):
        if isEnable:
            self.editMode = self.editMode | flag
        else:
            self.editMode = self.editMode &~ flag

    def isFocusFrameMode(self):
        return self.editMode | CanvasEditablePath.FocusFrameMode == self.editMode

    def isRoiEditableMode(self):
        return self.editMode | CanvasEditablePath.RoiEditableMode == self.editMode

    def isFrameEditableMode(self):
        return self.editMode | CanvasEditablePath.FrameEditableMode == self.editMode

    def isAdvanceSelectMode(self):
        return self.editMode | CanvasEditablePath.AdvanceSelectMode == self.editMode

    def __init__(self, parent:QGraphicsItem = None, isClosePath:bool = True) -> None:
        super().__init__(parent)
        self.editMode = CanvasEditablePath.RoiEditableMode | CanvasEditablePath.FrameEditableMode | CanvasEditablePath.FocusFrameMode | CanvasEditablePath.AdvanceSelectMode

        self.radius = 8
        self.m_borderWidth = 4
        self.roiRadius = self.m_borderWidth + 3
        # self.roiRadius = 5
        self.roiRadius = 1

        self.m_penDefault = QPen(Qt.white, self.m_borderWidth)
        self.m_penSelected = QPen(QColor("#FFFFA637"), self.m_borderWidth)
        self.m_instId = 0
        self.isClosePath = isClosePath

        self.initUI()

    def initUI(self):
        self.setEditableState(True)

        self.lastCursorDeque = deque()
        self.hoverCursor = Qt.SizeAllCursor

        self.roiItemList:list[CanvasROI] = []
        self.polygon = QPolygonF()
        self.shapePath = QPainterPath()

    def addPoint(self, point:QPointF, cursor:QCursor = Qt.PointingHandCursor) -> CanvasROI:
        self.m_instId += 1
        id = self.m_instId
        self.polygon.append(point)

        roiItem = CanvasROI(cursor, id, self)
        rect = QRectF(QPointF(0, 0), QSizeF(self.roiRadius*2, self.roiRadius*2))
        rect.moveCenter(point)
        roiItem.setRect(rect)

        self.roiItemList.append(roiItem)
        if not self.isRoiEditableMode():
            roiItem.hide()
        return roiItem

    def insertPoint(self, insertIndex:int, point:QPointF, cursor:QCursor = Qt.SizeAllCursor) -> CanvasROI:
        self.m_instId += 1
        id = self.m_instId

        self.polygon.insert(insertIndex, point)

        roiItem = CanvasROI(cursor, id, self)
        rect = QRectF(QPointF(0, 0), QSizeF(self.roiRadius*2, self.roiRadius*2))
        rect.moveCenter(point)
        roiItem.setRect(rect)

        self.roiItemList.insert(insertIndex, roiItem)
        return roiItem

    def removePoint(self, roiItem:CanvasROI):
        if not self.isRoiEditableMode():
            return

        # 如果是移除最后一个操作点，说明该路径将被移除
        if len(self.roiItemList) == 1:
            scene = self.scene()
            scene.removeItem(self)
            return

        index = self.roiItemList.index(roiItem)
        self.polygon.remove(index)
        self.roiItemList.remove(roiItem)
        self.scene().removeItem(roiItem)
        self.endResize(None)
        if len(self.roiItemList) > 0:
            self.setFocus(Qt.FocusReason.OtherFocusReason)

    def movePointById(self, roiItem:CanvasROI, localPos:QPointF):
        index = self.roiItemList.index(roiItem)
        self.prepareGeometryChange()
        self.polygon.replace(index, localPos)
        self.update()

    def moveRoiItemsBy(self, offset:QPointF):
        '''将所有的roiItem都移动一下'''
        for i in range(0, self.polygon.count()):
            roiItem:CanvasROI = self.roiItemList[i]
            roiItem.moveBy(-offset.x(), -offset.y())
            oldPos = self.polygon.at(i)
            newPos = oldPos - offset
            self.polygon.replace(i, newPos)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        painter.save()

        painter.setPen(self.m_penDefault if not self.hasFocusWrapper() or not self.isFocusFrameMode() else self.m_penSelected)
        painter.drawPolygon(self.polygon)

        # 绘制操作边框
        if self.hasFocusWrapper() and self.isFrameEditableMode():
            if self.roiRadius > 3:
                painter.setPen(QPen(Qt.red, 1, Qt.DashLine))
                painter.drawRect(self.polygon.boundingRect())

            painter.setPen(QPen(Qt.yellow, 1, Qt.DashLine))
            rect = self.getStretchableRect()
            painter.drawRect(rect)

        # 绘制路径虚线
        # if self.isAdvanceSelectMode():
        #     pen = QPen(Qt.green, 1, Qt.DashLine)
        #     pen.setDashPattern([10, 5])
        #     painter.setPen(pen)
        #     painter.drawPath(self.shapePath)

        painter.restore()

        if self.isFrameEditableMode():
            if self.hasFocusWrapper():
                self.initControllers()
            else:
                self.hideControllers()

    def hasFocusWrapper(self):
        # if self.hasFocus() or self.isSelected():
        if self.hasFocus():
            return True
        else:
            for value in self.roiItemList:
                roiItem:CanvasROI = value
                if roiItem.hasFocus():
                    return True

            if hasattr(self, 'controllers'):
                for controller in self.controllers:
                    if controller.hasFocus():
                        return True
        return False

    def calcOffset(self, startPoint:QPointF, endPoint:QPointF, dbRadious:float) -> QPointF:
        '''计算线段法向量，并且将其长度设为圆的半径，计算它们的偏移量'''
        v = QLineF(startPoint, endPoint)
        n = v.normalVector()
        n.setLength(dbRadious)
        return n.p1() - n.p2()

    # 修改光标选中的区域 https://doc.qt.io/qtforpython-5/PySide2/QtGui/QRegion.html
    def shape(self) -> QPainterPath:
        if self.hasFocusWrapper() and self.isFrameEditableMode():
            selectPath = QPainterPath()
            region = QRegion()
            rects = [self.boundingRect().toRect()]
            for value in self.roiItemList:
                roiItem:CanvasROI = value
                rects.append(roiItem.boundingRect().toRect())
            region.setRects(rects)
            selectPath.addRegion(region)
            return selectPath

        return self.shapePath

    def foreachPolygonSegments(self, callback:callable):
        for i in range(0, self.polygon.count()):
            points = []
            polygonPath = QPainterPath()
            startIndex = i
            endIndex = i + 1
            endIndex %= self.polygon.count()
            startPoint = self.polygon.at(startIndex)
            endPoint = self.polygon.at(endIndex)

            offset = self.calcOffset(startPoint, endPoint, self.roiRadius)

            points.append(startPoint - offset)
            points.append(startPoint + offset)
            points.append(endPoint + offset)
            points.append(endPoint - offset)

            polygonPath.addPolygon(QPolygonF(points))
            polygonPath.closeSubpath()
            if callback(startIndex, endIndex, polygonPath):
                break

            if self.polygon.count() < 3:
                break

    def boundingRect(self) -> QRectF:
        self.shapePath.clear()

        if self.isAdvanceSelectMode():
            def appendShapePath(startIndex, endIndex, polygonPath):
                self.shapePath.addPath(polygonPath)
                return False

            self.foreachPolygonSegments(appendShapePath)
        else:
            points = []
            for i in range(0, self.polygon.count()):
                points.append(self.polygon.at(i))

            CanvasUtil.buildSegmentsPath(self.shapePath, points, self.isClosePath)

        return self.shapePath.boundingRect()


    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.lastCursorDeque.append(self.cursor())
        self.setCursor(self.hoverCursor)
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        if len(self.lastCursorDeque) > 0:
            lastCursor = self.lastCursorDeque.pop()
            self.setCursor(lastCursor)
        return super().hoverLeaveEvent(event)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:

            def hitTest(startIndex, endIndex, polygonPath:QPainterPath):
                if polygonPath.contains(event.pos()):
                    self.insertPoint(endIndex, event.pos(), Qt.CursorShape.SizeBDiagCursor)
                    return True
                return False

            self.foreachPolygonSegments(hitTest)
        return super().mouseDoubleClickEvent(event)

    def initControllers(self):
        if not self.isFrameEditableMode():
            return

        if not hasattr(self, "controllers"):
            self.controllers:list[CanvasEllipseItem] = []

        rect = self.getStretchableRect()
        size = QSizeF(self.radius*2, self.radius*2)
        posTypes = [
            [EnumPosType.ControllerPosTL, Qt.CursorShape.SizeFDiagCursor], 
            [EnumPosType.ControllerPosTC, Qt.CursorShape.SizeVerCursor], 
            [EnumPosType.ControllerPosTR, Qt.CursorShape.SizeBDiagCursor], 
            [EnumPosType.ControllerPosRC, Qt.CursorShape.SizeHorCursor], 
            [EnumPosType.ControllerPosBR, Qt.CursorShape.SizeFDiagCursor], 
            [EnumPosType.ControllerPosBC, Qt.CursorShape.SizeVerCursor], 
            [EnumPosType.ControllerPosBL, Qt.CursorShape.SizeBDiagCursor], 
            [EnumPosType.ControllerPosLC, Qt.CursorShape.SizeHorCursor],
            [EnumPosType.ControllerPosTT, Qt.CursorShape.PointingHandCursor],
            ]

        if len(self.controllers) == 0:
            for info in posTypes:
                # controller = CanvasEllipseItem(info[-1], self)
                controller = CanvasEllipseItem(info[-1], self)
                controller.setRectWrapper(rect, info[0], self.radius, size)
                self.controllers.append(controller)
        else:
            for controller in self.controllers:
                controller.resetPosition(rect, self.radius, size)
                if not controller.isVisible():
                    controller.show()

    def hideControllers(self):
        if not hasattr(self, "controllers"):
            return
        for controller in self.controllers:
            if controller.isVisible():
                controller.hide()

    def mouseMoveRotateOperator(self, scenePos:QPointF, localPos:QPointF) -> None:
        p1 = QLineF(self.originPos, self.m_pressPos)
        p2 = QLineF(self.originPos, localPos)

        dRotateAngle = p2.angleTo(p1)

        dCurAngle = self.rotation() + dRotateAngle
        while dCurAngle > 360.0:
            dCurAngle -= 360.0
        self.setRotation(dCurAngle)
        self.update()

    def getStretchableRect(self) -> QRect:
        return self.polygon.boundingRect() + QMarginsF(self.roiRadius, self.roiRadius, self.roiRadius, self.roiRadius)

    def updateEdge(self, currentPosType, localPos:QPoint):
        offset = -self.roiRadius
        lastRect = self.polygon.boundingRect().toRect()
        newRect = lastRect.adjusted(0, 0, 0, 0)
        if currentPosType == EnumPosType.ControllerPosTL:
            localPos += QPoint(-offset, -offset)
            newRect.setTopLeft(localPos)
        elif currentPosType == EnumPosType.ControllerPosTC:
            localPos += QPoint(0, -offset)
            newRect.setTop(localPos.y())
        elif currentPosType == EnumPosType.ControllerPosTR:
            localPos += QPoint(offset, -offset)
            newRect.setTopRight(localPos)
        elif currentPosType == EnumPosType.ControllerPosRC:
            localPos += QPoint(offset, 0)
            newRect.setRight(localPos.x())
        elif currentPosType == EnumPosType.ControllerPosBR:
            localPos += QPoint(offset, offset)
            newRect.setBottomRight(localPos)
        elif currentPosType == EnumPosType.ControllerPosBC:
            localPos += QPoint(0, offset)
            newRect.setBottom(localPos.y())
        elif currentPosType == EnumPosType.ControllerPosBL:
            localPos += QPoint(-offset, offset)
            newRect.setBottomLeft(localPos)
        elif currentPosType == EnumPosType.ControllerPosLC:
            localPos = localPos - QPoint(offset, offset)
            newRect.setLeft(localPos.x())

        xScale = newRect.width() / max(lastRect.width(), 1)
        yScale = newRect.height() / max(lastRect.height(), 1)

        for i in range(0, self.polygon.count()):
            oldPos = self.polygon.at(i)

            if currentPosType == EnumPosType.ControllerPosTC:
                yPos = oldPos.y() - abs(oldPos.y() - lastRect.bottomRight().y()) * (yScale - 1)
                newPos = QPointF(oldPos.x(), yPos)
            elif currentPosType == EnumPosType.ControllerPosBC:
                yPos = oldPos.y() + abs(oldPos.y() - lastRect.topLeft().y()) * (yScale - 1)
                newPos = QPointF(oldPos.x(), yPos)
            elif currentPosType == EnumPosType.ControllerPosLC:
                xPos = oldPos.x() - abs(oldPos.x() - lastRect.bottomRight().x()) * (xScale - 1)
                newPos = QPointF(xPos, oldPos.y())
            elif currentPosType == EnumPosType.ControllerPosRC:
                xPos = oldPos.x() + abs(oldPos.x() - lastRect.topLeft().x()) * (xScale - 1)
                newPos = QPointF(xPos, oldPos.y())
            elif currentPosType == EnumPosType.ControllerPosTL:
                xPos = oldPos.x() - abs(oldPos.x() - lastRect.bottomRight().x()) * (xScale - 1)
                yPos = oldPos.y() - abs(oldPos.y() - lastRect.bottomRight().y()) * (yScale - 1)
                newPos = QPointF(xPos, yPos)
            elif currentPosType == EnumPosType.ControllerPosTR:
                xPos = oldPos.x() + abs(oldPos.x() - lastRect.topLeft().x()) * (xScale - 1)
                yPos = oldPos.y() - abs(oldPos.y() - lastRect.bottomRight().y()) * (yScale - 1)
                newPos = QPointF(xPos, yPos)
            elif currentPosType == EnumPosType.ControllerPosBR:
                xPos = oldPos.x() + abs(oldPos.x() - lastRect.topLeft().x()) * (xScale - 1)
                yPos = oldPos.y() + abs(oldPos.y() - lastRect.topLeft().y()) * (yScale - 1)
                newPos = QPointF(xPos, yPos)
            elif currentPosType == EnumPosType.ControllerPosBL:
                xPos = oldPos.x() - abs(oldPos.x() - lastRect.bottomRight().x()) * (xScale - 1)
                yPos = oldPos.y() + abs(oldPos.y() - lastRect.topLeft().y()) * (yScale - 1)
                newPos = QPointF(xPos, yPos)

            roiItem:CanvasROI = self.roiItemList[i]
            rect = roiItem.rect()
            rect.moveCenter(self.mapToItem(roiItem, newPos))
            roiItem.setRect(rect)

            self.polygon.replace(i, newPos)

        self.update()

    def startResize(self, localPos:QPointF) -> None:
        pass

    def endResize(self, localPos:QPointF) -> None:
        self.prepareGeometryChange()

        rect = self.shapePath.boundingRect()
        # 计算正常旋转角度（0度）下，中心的的坐标
        oldCenter = QPointF(self.x()+rect.x()+rect.width()/2, self.y()+rect.y()+rect.height()/2)
        # 计算旋转后，中心坐标在view中的位置
        newCenter = self.mapToScene(rect.center())
        # 设置正常坐标减去两个坐标的差
        difference = oldCenter-newCenter
        self.setPos(self.x()-difference.x(), self.y()-difference.y())
        # 最后设置旋转中心
        self.setTransformOriginPoint(rect.center())

        self.update()

    def endResizeOld(self, localPos:QPointF) -> None:
        self.prepareGeometryChange()
        # 解决有旋转角度的矩形，拉伸之后，再次旋转，旋转中心该仍然为之前坐标，手动设置为中心，会产生漂移的问题
        rect = self.shapePath.boundingRect()
        angle = math.radians(self.rotation())

        p1 = rect.center()
        origin = self.transformOriginPoint()
        p2 = QPointF(0, 0)

        p2.setX(origin.x() + math.cos(angle)*(p1.x() - origin.x()) - math.sin(angle)*(p1.y() - origin.y()))
        p2.setY(origin.y() + math.sin(angle)*(p1.x() - origin.x()) + math.cos(angle)*(p1.y() - origin.y()))

        diff:QPointF = p1 - p2
        if diff.isNull():
            return

        self.moveRoiItemsBy(diff)
        self.setTransformOriginPoint(p1-diff)

        self.update()

    def startRotate(self, localPos:QPointF) -> None:
        self.originPos = self.boundingRect().center()
        self.setTransformOriginPoint(self.originPos)
        self.m_pressPos = localPos
    
    def endRotate(self, localPos:QPointF) -> None:
        pass

    def setEditableState(self, isEditable:bool):
        '''设置可编辑状态'''
        self.setFlag(QGraphicsItem.ItemIsMovable, isEditable)
        self.setFlag(QGraphicsItem.ItemIsSelectable, isEditable)
        self.setFlag(QGraphicsItem.ItemIsFocusable, isEditable)
        self.setAcceptHoverEvents(isEditable)