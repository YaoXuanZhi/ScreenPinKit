from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QMouseEvent, QPaintEvent, QPainter
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QGraphicsSceneMouseEvent
import numpy as np

class SmoothCurveGenerator:
    @staticmethod
    def generateSmoothCurve(points, closed, tension, numberOfSegments):
        ps = [p.x() for p in points] + [p.y() for p in points]
        return SmoothCurveGenerator._generateSmoothCurve(ps, closed, tension, numberOfSegments)

    @staticmethod
    def _generateSmoothCurve(ps, closed, tension, numberOfSegments):
        result = []
        if closed:
            ps = [ps[-2], ps[-1]] + ps + [ps[0], ps[1]]
        else:
            ps = [ps[1], ps[0]] + ps + [ps[-2], ps[-1]]

        for i in range(2, len(ps) - 4, 2):
            t1x = (ps[i + 2] - ps[i - 2]) * tension
            t2x = (ps[i + 4] - ps[i]) * tension
            t1y = (ps[i + 3] - ps[i - 1]) * tension
            t2y = (ps[i + 5] - ps[i + 1]) * tension

            for t in range(numberOfSegments + 1):
                st = t / numberOfSegments
                c1 = 2 * pow(st, 3) - 3 * pow(st, 2) + 1
                c2 = -2 * pow(st, 3) + 3 * pow(st, 2)
                c3 = pow(st, 3) - 2 * pow(st, 2) + st
                c4 = pow(st, 3) - pow(st, 2)

                x = c1 * ps[i] + c2 * ps[i + 2] + c3 * t1x + c4 * t2x
                y = c1 * ps[i + 1] + c2 * ps[i + 3] + c3 * t1y + c4 * t2y

                result.append(x)
                result.append(y)

        if closed:
            path = QPainterPath()
            path.moveTo(result[0], result[1])
            for i in range(2, len(result) - 2, 2):
                path.lineTo(result[i], result[i + 1])
            path.closeSubpath()
            return path
        else:
            return [QPointF(result[i], result[i + 1]) for i in range(0, len(result), 2)]

    @staticmethod
    def buildSmoothCurve(_points, offset = 0.33):
        # 创建一个路径对象
        path = QPainterPath()
        path.moveTo(_points[0])

        # 绘制平滑的曲线
        for i in range(1, len(_points)):
            # 计算控制点，以便曲线在点之间平滑过渡
            controlPoint1 = SmoothCurveGenerator.calculateControlPoint(_points[i - 1], _points[i], offset)
            controlPoint2 = SmoothCurveGenerator.calculateControlPoint(_points[i - 1], _points[i], offset * -1)

            # path.quadTo(controlPoint2, self._points[i])
            # path.quadTo(controlPoint1, controlPoint2, self._points[i])
            # path.quadTo(controlPoint1, self._points[i])
            path.cubicTo(controlPoint1, controlPoint2, _points[i])

        return path

    @staticmethod
    def calculateControlPoint(startPoint, endPoint, offset):
        # 计算控制点的位置，以便曲线平滑过渡
        dx = endPoint.x() - startPoint.x()
        dy = endPoint.y() - startPoint.y()
        return QPoint(startPoint.x() + dx * offset, startPoint.y() + dy * offset)

    @staticmethod
    def fitCurve(points:list):
        '''拟合曲线'''

        # # 将原始数据点转换为NumPy数组
        # x_data, y_data = zip(*points)
        # x_data = np.array(x_data)
        # y_data = np.array(y_data)

        # 将原始数据点转换为NumPy数组
        x_data = np.array([point.x() for point in points])
        y_data = np.array([point.y() for point in points])

        # 多项式拟合
        degree = 2  # 多项式次数
        coefficients = np.polyfit(x_data, y_data, degree)

        # 构建拟合曲线的路径
        path = QPainterPath()
        for x in range(int(min(x_data)), int(max(x_data)) + 1):
            y = np.polyval(coefficients, x)
            if y < min(y_data):
                y = min(y_data)
            elif y > max(y_data):
                y = max(y_data)
            if x == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)


        # 多项式拟合
        degree = 2  # 多项式次数
        coefficients = np.polyfit(x_data, y_data, degree)

        # 构建拟合曲线的路径
        path = QPainterPath()
        for x in range(int(min(x_data)), int(max(x_data)) + 1):
            y = np.polyval(coefficients, x)
            if y < min(y_data):
                y = min(y_data)
            elif y > max(y_data):
                y = max(y_data)
            if x == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)

        return path

class DrawingScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(DrawingScene, self).__init__(parent)

        self.pathItem = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.pathItem == None:
                self.pathItem = QGraphicsPathItem()
                # self.pathItem.setBrush(QBrush(QColor(255, 0, 0, 100)))
                self.pathItem.setPen(QPen(QColor(255, 0, 0), 3, Qt.SolidLine))
                self.path = QPainterPath()
                self.path.moveTo(event.scenePos())
                self.addItem(self.pathItem)
                self.points = []

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.path.lineTo(event.scenePos())
            self.pathItem.setPath(self.path)
            self.points.append(event.scenePos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            closed = True
            tension = 0.5
            numberOfSegments = 20
            # smoothCurve = SmoothCurveGenerator.generateSmoothCurve(self.points, closed, tension, numberOfSegments)
            # smoothCurve = SmoothCurveGenerator.buildSmoothCurve(self.points)
            # self.pathItem.setPath(smoothCurve)
            # self.points.clear()
            smoothCurve = SmoothCurveGenerator.fitCurve(self.points)
            self.pathItem.setPath(smoothCurve)
            self.points.clear()
            self.pathItem = None

class DrawingView(QGraphicsView):
    def __init__(self, scene:QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.initUI()

    def initUI(self):
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.scene_width, self.scene_height = 64000, 64000
        self.scene().setSceneRect(-self.scene_width//2, -self.scene_height//2, self.scene_width, self.scene_height)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        # self.setDragMode(QGraphicsView.RubberBandDrag)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    scene = DrawingScene()
    view = DrawingView(scene)
    view.show()
    sys.exit(app.exec_())