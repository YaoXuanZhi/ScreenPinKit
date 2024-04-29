import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtGui import QIcon
from qframelesswindow import FramelessWindow
from PyQt5.QtSvg import QSvgWidget
from qfluentwidgets import PrimaryPushButton, SplitTitleBar, PushButton

class SvgImageViewer(FramelessWindow, QWidget):
    def __init__(self, folder_path):
        super().__init__()
        self.setTitleBar(SplitTitleBar(self))
        self.titleBar.raise_()

        self.folder_path = folder_path
        self.image_list = self.get_svg_files()
        self.current_index = 0

        self.image_label = QSvgWidget()
        self.next_button = PrimaryPushButton("下一张")
        self.prev_button = PrimaryPushButton("上一张")

        self.next_button.clicked.connect(self.show_next_image)
        self.prev_button.clicked.connect(self.show_previous_image)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.next_button)
        layout.addWidget(self.prev_button)


        self.iconButton = PushButton('图标')
        self.iconButton.resize(200, 200)
        layout.addWidget(self.iconButton)

        self.setLayout(layout)
        self.show_current_image()

    def get_svg_files(self):
        svg_files = []
        for file_name in os.listdir(self.folder_path):
            if file_name.endswith(".svg"):
                svg_files.append(os.path.join(self.folder_path, file_name))
        return svg_files

    def show_current_image(self):
        image_path = self.image_list[self.current_index]
        self.image_label.load(image_path)

        self.iconButton.setIcon(QIcon(image_path))

    def show_next_image(self):
        self.current_index = (self.current_index + 1) % len(self.image_list)
        self.show_current_image()

    def show_previous_image(self):
        self.current_index = (self.current_index - 1) % len(self.image_list)
        self.show_current_image()

if __name__ == "__main__":
    app = QApplication([])
    svgPath = os.path.join(os.path.dirname(__file__), "resources")
    viewer = SvgImageViewer(svgPath)
    viewer.show()
    app.exec_()