# coding=utf-8
import os
import sys, math, typing
from enum import Enum
from datetime import datetime
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from qfluentwidgets import (RoundMenu, Action, FluentIcon, InfoBar, InfoBarPosition, CommandBarView, Flyout, FlyoutAnimationType, TeachingTip, TeachingTipTailPosition, TeachingTipView)
from icon import ScreenShotIcon
from qfluentwidgets import *

from canvas_editor import CanvasEditor, DrawActionEnum
from canvas_item import *

# 拖曳移动窗口类
class QDragWindow(QLabel):
    def __init__(self, parent:QWidget):
        super().__init__(parent)
        self.drag = False

    @typing.overload
    def isAllowDrag(self):
        return False

    def startDrag(self):
        pass

    def endDrag(self):
        pass

    def mousePressEvent(self, event):
        if not self.isAllowDrag():
            return super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag = True
            self.posX, self.posY = event.x(), event.y()
            self.startDrag()

    def mouseReleaseEvent(self, event):
        if not self.isAllowDrag():
            return super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag = False
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            self.endDrag()

    def mouseMoveEvent(self, event):
        if not self.isAllowDrag():
            return super().mouseMoveEvent(event)
        if self.isVisible():
            if self.drag:
                self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
                self.move(event.x() + self.x() - self.posX, event.y() + self.y() - self.posY)

# 贴图控件
class QPixmapWidget(QLabel):
    def __init__(self, parent=None, physicalPixmap:QPixmap=None, xRadius:float=20, yRadius:float=20):
        super().__init__(parent)
        self.setFocusPolicy(Qt.ClickFocus)
        self.physicalPixmap = physicalPixmap
        self.xRadius = xRadius
        self.yRadius = yRadius
        self.painter = QPainter()

    def paintEvent(self, e):
        if self.physicalPixmap == None:
            return super().paintEvent(e)

        canvasPixmap = self.physicalPixmap.copy()
        self.painter.begin(self)
        self.painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        clipPath = QPainterPath()
        clipPath.addRoundedRect(QRectF(self.rect()), self.xRadius, self.yRadius)
        self.painter.setClipPath(clipPath)
        self.painter.drawPixmap(self.rect(), canvasPixmap)
        self.painter.end()

# 绘制动作
class DrawAction():
    def __init__(self, actionEnum:DrawActionEnum, painterTool:QWidget, callback=None) -> None:
        self.actionEnum:DrawActionEnum = actionEnum
        self.painterTool = painterTool
        self.callback = callback

    def switchEditState(self, isEdit:bool):
        if self.callback != None:
            self.callback(isEdit)

# 绘图控件
class QPainterWidget(QPixmapWidget):
    def __init__(self, parent=None, physicalPixmap:QPixmap=None, xRadius:float=20, yRadius:float=20):
        super().__init__(parent, physicalPixmap, xRadius, yRadius)
        self.toolbar:QWidget = None
        self.actionGroup:QActionGroup = None
        self.drawWidget:CanvasEditor = None
        self.sceneBrush:QBrush = None
        self.clearDraw(True)
        self.initLayout()

    def initLayout(self):
        self.contentLayout = QVBoxLayout()
        self.contentLayout.setAlignment(Qt.AlignHCenter)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.contentLayout)

        if self.physicalPixmap != None:
            basePixmap = self.physicalPixmap.copy()
            self.sceneBrush = QBrush(basePixmap)
            screenDevicePixelRatio = QApplication.primaryScreen().grabWindow(0).devicePixelRatio()
            transform = QtGui.QTransform()
            transform.scale(1/screenDevicePixelRatio, 1/screenDevicePixelRatio)
            transform.translate(-basePixmap.size().width()/2, -basePixmap.size().height()/2)
            self.sceneBrush.setTransform(transform)

    def getCommandBarPosition(self) -> TeachingTipTailPosition:
        return TeachingTipTailPosition.TOP_RIGHT

    def showComplexFlyout(self, targetWidget:QWidget = None):
        class FlyoutView2(FlyoutViewBase):
            """ Flyout view """

            closed = pyqtSignal()

            def __init__(self, title: str, content: str, icon: QIcon = None,
                        image: QImage = None, isClosable=False, parent=None):
                super().__init__(parent=parent)
                self.icon = icon
                self.title = title
                self.image = image
                self.content = content
                self.isClosable = isClosable

                self.vBoxLayout = QVBoxLayout(self)
                self.viewLayout = QHBoxLayout()
                self.widgetLayout = QVBoxLayout()

                self.titleLabel = QLabel(title, self)
                self.contentLabel = QLabel(content, self)
                # self.iconWidget = IconWidget(icon, self)
                # self.imageLabel = ImageLabel(self)
                # self.closeButton = TransparentToolButton(FluentIcon.CLOSE, self)

                self.__initWidgets()

            def __initWidgets(self):
                # self.imageLabel.setImage(self.image)

                # self.closeButton.setFixedSize(32, 32)
                # self.closeButton.setIconSize(QSize(12, 12))
                # self.closeButton.setVisible(self.isClosable)
                self.titleLabel.setVisible(bool(self.title))
                self.contentLabel.setVisible(bool(self.content))
                # self.iconWidget.setHidden(self.icon is None)

                # self.closeButton.clicked.connect(self.closed)

                self.titleLabel.setObjectName('titleLabel')
                self.contentLabel.setObjectName('contentLabel')
                # FluentStyleSheet.TEACHING_TIP.apply(self)

                self.__initLayout()

            def __initLayout(self):
                self.vBoxLayout.setContentsMargins(1, 1, 1, 1)
                self.widgetLayout.setContentsMargins(0, 8, 0, 8)
                self.viewLayout.setSpacing(4)
                self.widgetLayout.setSpacing(0)
                self.vBoxLayout.setSpacing(0)

                # # add icon widget
                # if not self.title or not self.content:
                #     self.iconWidget.setFixedHeight(36)

                self.vBoxLayout.addLayout(self.viewLayout)
                # self.viewLayout.addWidget(self.iconWidget, 0, Qt.AlignTop)

                # add text
                self._adjustText()
                self.widgetLayout.addWidget(self.titleLabel)
                self.widgetLayout.addWidget(self.contentLabel)
                self.viewLayout.addLayout(self.widgetLayout)

                # add close button
                # self.closeButton.setVisible(self.isClosable)
                # self.viewLayout.addWidget(
                #     self.closeButton, 0, Qt.AlignRight | Qt.AlignTop)

                # adjust content margins
                margins = QMargins(6, 5, 6, 5)
                margins.setLeft(20 if not self.icon else 5)
                margins.setRight(20 if not self.isClosable else 6)
                self.viewLayout.setContentsMargins(margins)

                # add image
                self._adjustImage()
                self._addImageToLayout()

            def addWidget(self, widget: QWidget, stretch=0, align=Qt.AlignLeft):
                """ add widget to view """
                self.widgetLayout.addSpacing(8)
                self.widgetLayout.addWidget(widget, stretch, align)

            def _addImageToLayout(self):
                # self.imageLabel.setBorderRadius(8, 8, 0, 0)
                # self.imageLabel.setHidden(self.imageLabel.isNull())
                # self.vBoxLayout.insertWidget(0, self.imageLabel)

                radioWidget = QWidget()
                radioLayout = QVBoxLayout(radioWidget)
                radioLayout.setContentsMargins(2, 0, 0, 0)
                radioLayout.setSpacing(15)
                radioButton1 = RadioButton(self.tr('Star Platinum'), radioWidget)
                radioButton2 = RadioButton(self.tr('Crazy Diamond'), radioWidget)
                radioButton3 = RadioButton(self.tr('Soft and Wet'), radioWidget)
                buttonGroup = QButtonGroup(radioWidget)
                buttonGroup.addButton(radioButton1)
                buttonGroup.addButton(radioButton2)
                buttonGroup.addButton(radioButton3)
                radioLayout.addWidget(radioButton1)
                radioLayout.addWidget(radioButton2)
                radioLayout.addWidget(radioButton3)
                radioButton1.click()
                # self.vBoxLayout.insertWidget(0, radioWidget)
                self.viewLayout.addWidget(radioWidget)
                pass

            def _adjustText(self):
                w = min(900, QApplication.screenAt(
                    QCursor.pos()).geometry().width() - 200)

                # adjust title
                chars = max(min(w / 10, 120), 30)
                self.titleLabel.setText(self.title)

                # adjust content
                chars = max(min(w / 9, 120), 30)
                self.contentLabel.setText(self.content)

            def _adjustImage(self):
                w = self.vBoxLayout.sizeHint().width() - 2
                # self.imageLabel.scaledToWidth(w)

            def showEvent(self, e):
                super().showEvent(e)
                self._adjustImage()
                self.adjustSize()

        view = FlyoutView2(
            title=self.tr('Julius·Zeppeli'),
            content=self.tr("测试文本"),
            image=':/gallery/images/SBR.jpg',
        )

        # add button to view
        button = PushButton('Action')
        button.setFixedWidth(120)
        view.addWidget(button, align=Qt.AlignRight)

        # adjust layout (optional)
        view.widgetLayout.insertSpacing(1, 5)
        view.widgetLayout.insertSpacing(0, 5)
        view.widgetLayout.addSpacing(5)

        if targetWidget == None:
            targetWidget = self.window()
            targetWidget = self.parentWidget()

        # show view
        # Flyout.make(view, self.complexFlyoutButton, self.window(), FlyoutAnimationType.SLIDE_RIGHT)
        # Flyout.make(view, self.window(), self.window(), FlyoutAnimationType.DROP_DOWN)
        # Flyout.make(view, self.complexFlyoutButton, self.window(), FlyoutAnimationType.PULL_UP)
        # self.toolbar = Flyout.make(view, self.window(), self.window(), FlyoutAnimationType.PULL_UP)
        # self.toolbar = Flyout.make(view, self.parentWidget(), self.parentWidget(), FlyoutAnimationType.PULL_UP)
        # pixmap, rect = canvas_util.CanvasUtil.grabScreens()
        # # topCenter = (rect.topLeft() + rect.topRight()) / 2
        # topCenter = rect.center()
        # Flyout.make(view, topCenter, self, FlyoutAnimationType.PULL_UP)
        # Flyout.make(view, targetWidget, self, FlyoutAnimationType.SLIDE_LEFT)
        TeachingTip.make(
            target=targetWidget,
            view=view,
            duration=-1,
            tailPosition=TeachingTipTailPosition.TOP_LEFT,
            parent=self
        )

    def showCommandBar(self):
        if self.toolbar != None:
            self.toolbar.show()
            self.drawWidget.switchDrawTool(DrawActionEnum.DrawNone)
            return

        position = self.getCommandBarPosition()
        view = CommandBarView(self)
        closeAction = Action(ScreenShotIcon.FINISHED, '完成绘画')

        drawActions = [
            Action(ScreenShotIcon.RECTANGLE, '矩形', triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawRectangle)),
            Action(ScreenShotIcon.POLYGONAL_LINE, '折线', triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawPolygonalLine)),
            Action(ScreenShotIcon.GUIDE, '标记', triggered=lambda: self.switchDrawTool(DrawActionEnum.UseMarkerItem)),
            Action(ScreenShotIcon.POLYGON, '图案', triggered=lambda: self.switchDrawTool(DrawActionEnum.PasteSvg)),
            Action(ScreenShotIcon.ARROW, '箭头', triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawArrow)),
            Action(ScreenShotIcon.STAR, '五角星', triggered=lambda: self.switchDrawTool(DrawActionEnum.DrawStar)),
            Action(ScreenShotIcon.MARKER_PEN, '记号笔', triggered=lambda: self.switchDrawTool(DrawActionEnum.UseMarkerPen)),
            Action(ScreenShotIcon.PENCIL, '铅笔', triggered=lambda: self.switchDrawTool(DrawActionEnum.UsePencil)),
            Action(ScreenShotIcon.TEXT, '文本', triggered=lambda: self.switchDrawTool(DrawActionEnum.EditText)),
            Action(ScreenShotIcon.ERASE, '橡皮擦', triggered=lambda: self.switchDrawTool(DrawActionEnum.UseEraser)),
        ]

        self.actionGroup = QActionGroup(self)
        for action in drawActions:
            action.setCheckable(True)
            self.actionGroup.addAction(action)

        view.addActions(drawActions)
        view.addSeparator()
        view.addActions([
            Action(ScreenShotIcon.DELETE_ALL, '清除绘画', triggered=self.clearDraw),
            # Action(ScreenShotIcon.UNDO2, '撤销', triggered=self.undo),
            # Action(ScreenShotIcon.REDO2, '重做', triggered=self.redo),
            closeAction,
        ])

        view.hBoxLayout.setContentsMargins(1, 1, 1, 1)
        view.setIconSize(QSize(20, 20))

        view.resizeToSuitableWidth()
        self.toolbar = TeachingTip.make(
            target=self,
            view=view,
            duration=-1,
            tailPosition=position,
            parent=self
        )

        closeAction.triggered.connect(self.completeDraw)

        self.initDrawLayer()
        self.showComplexFlyout(view)

    def initDrawLayer(self):
        if self.drawWidget != None: 
            return

        self.drawWidget = CanvasEditor(self, self.sceneBrush)
        self.drawWidget.initUI()
        self.contentLayout.addWidget(self.drawWidget)

    def completeDraw(self):
        if self.toolbar != None:
            self.clearDrawFlag()
            self.toolbar.close()
            self.toolbar.destroy()
            self.toolbar = None
            self.drawWidget.quitDraw()

    def closeEvent(self, event):
        super().closeEvent(event)
        self.completeDraw()

    def keyPressEvent(self, event) -> None:
        # 监听ESC键，当按下ESC键时，逐步取消编辑状态
        if event.key() == Qt.Key_Escape:
            # 如果当前绘图工具不在编辑状态，则本次按下Esc键会关掉绘图工具条
            if self.currentDrawActionEnum != DrawActionEnum.DrawNone:
                self.clearDrawFlag()
                self.drawWidget.quitDraw()
            elif self.toolbar != None and self.toolbar.isVisible():
                self.completeDraw()
            else:
                self.destroyImage()

    def contextMenuEvent(self, event:QtGui.QContextMenuEvent):
        if self.currentDrawActionEnum != DrawActionEnum.DrawNone:
            return
        menu = RoundMenu(parent=self)
        menu.addActions([
            Action(ScreenShotIcon.WHITE_BOARD, '标注', triggered=self.showCommandBar),
            Action(ScreenShotIcon.COPY, '复制', triggered=self.copyToClipboard),
            Action(ScreenShotIcon.CLICK_THROUGH, '鼠标穿透', triggered=self.clickThrough),
        ])
        menu.view.setIconSize(QSize(20, 20))
        menu.exec(event.globalPos())

    def checkDrawActionChange(self):
        # 如果中途切换了绘图工具，则关闭上一个绘图工具的编辑状态
        if len(self.drawActions) > 0 and self.drawActions[-1].actionEnum != self.currentDrawActionEnum:
            self.setDrawActionEditable(self.drawActions[-1].actionEnum, False)
            self.createCustomInfoBar(f"绘图工具切换到 【{self.currentDrawActionEnum.value}】")

    def addDrawAction(self, drawAction:DrawAction):
        self.drawActions.append(drawAction)

    def setDrawActionEditable(self, drawFlag:DrawActionEnum, isEdit:bool):
        for action in self.drawActions:
            if action.actionEnum == drawFlag:
                action.switchEditState(isEdit)

    def undo(self):
        self.createCustomInfoBar(f"【撤销】待支持")

    def clickThrough(self):
        self.parentWidget().setMouseThroughState(True)

    def redo(self):
        self.createCustomInfoBar(f"【重做】待支持")

    def destroyImage(self):
        self.parentWidget().close()

    # 得到最终绘制后的Pixmap
    def getFinalPixmap(self) -> QPixmap:
        # 经测试，这种方式截屏会有概率出现白边，推测是精度问题导致的，遂改成下面的实现
        # return self.grab()
        
        basePixmap = self.physicalPixmap.copy()
        painter = QPainter()
        painter.begin(basePixmap)
        if self.drawWidget != None:
            painter.drawPixmap(self.drawWidget.geometry(), self.drawWidget.grab())
        painter.end()
        return basePixmap
        
    def copyToClipboard(self):
        finalPixmap = self.getFinalPixmap()
        QApplication.clipboard().setPixmap(finalPixmap)

    def switchDrawTool(self, drawActionEnum:DrawActionEnum, cursor:QCursor = Qt.CursorShape.CrossCursor):
        self.drawWidget.switchDrawTool(drawActionEnum)
        self.currentDrawActionEnum = drawActionEnum 
        self.checkDrawActionChange()
        self.setCursor(cursor)
        if len(self.drawActions) > 0 and self.drawActions[-1].actionEnum == DrawActionEnum.DrawRectangle:
            # 如果上一个绘图工具是绘制矩形，则切换到编辑状态
            self.drawActions[-1].switchEditState(True)
        else:
            self.addDrawAction(DrawAction(drawActionEnum, None))

    def clearDraw(self, isInit:bool=False):
        if not isInit:
            if hasattr(self, "drawWidget"):
                self.drawWidget.close()
                self.drawWidget.destroy()
                self.drawWidget = None
                self.initDrawLayer()

        self.drawActions: list[DrawAction] = []
        self.clearDrawFlag()

    def focusInEvent(self, event:QFocusEvent) -> None:
        self.parentWidget().focused = True
        self.parentWidget().update()

    def focusOutEvent(self, event:QFocusEvent) -> None:
        # 获取鼠标居于屏幕上的位置点
        pos = QCursor.pos()

        # 计算绘图区和工具区的并集
        painterRect = QRect(self.mapToGlobal(self.rect().topLeft()), self.mapToGlobal(self.rect().bottomRight()))
        rects = [painterRect]
        if self.toolbar != None:
            toolbarRect = QRect(self.toolbar.mapToGlobal(self.toolbar.rect().topLeft()), self.toolbar.mapToGlobal(self.toolbar.rect().bottomRight()))
            rects.append(toolbarRect)
        region = QRegion()
        region.setRects(rects)

        # 经测试发现，焦点非常容易变化，但是我们在绘图区和工具区的操作引起的焦点丢失得屏蔽掉
        if not region.contains(pos):
            self.parentWidget().focused = False
            self.parentWidget().update()

    def clearDrawFlag(self):
        self.currentDrawActionEnum = DrawActionEnum.DrawNone
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

        if self.actionGroup != None:
            for action in self.actionGroup.actions():
                action.setChecked(False)

    def createCustomInfoBar(self, text:str):
        w = InfoBar.new(
            icon=ScreenShotIcon.GUIDE,
            title='',
            content=text,
            orient=Qt.Horizontal,
            isClosable=False,
            position=InfoBarPosition.BOTTOM,
            duration=1000,
            parent=self
        )
        # w.iconWidget.setFixedSize(QSize(40, 40))
        w.setCustomBackgroundColor('white', '#202020')
