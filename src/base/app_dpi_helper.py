# coding=utf-8
import sys, os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class AppDpiHelper:
    """
    Dpi辅助类

    在Qt之中，必须在QApplication(sys.argv)之前就设置Dpi，否则不会生效，
    但是要获得准确的DpiScale，又需要用到QApplication，因此需要重启一次程序才能让
    指定的DpiScale生效，至于为何不采用Qt.AA_EnableHighDpiScaling来实现高Dpi支持呢，
    这是因为引入了它，会导致非常多额外处理的情况，而且只能见招拆招，实在顶不住放弃了
    """

    @staticmethod
    def checkDpiAndRestartApplication():
        """
        获得当前DpiScale，作为二次启动时的传参，重启应用

        Note:
            ide调试器运行该函数会导致调试器停止，因此额外新增了--debug参数，用于调试
        """
        app = QApplication(sys.argv)
        screen = app.primaryScreen()
        dpiScale = screen.logicalDotsPerInch() / 96.0
        app.exit()

        python = sys.executable
        sys.argv.append("--restarted")
        sys.argv.append(f"--dpi-scale={dpiScale}")
        QProcess.startDetached(python, sys.argv)

    @staticmethod
    def extractDpiScale(args):
        """从命令行参数里提取出DpiScale"""
        for arg in args:
            if arg.startswith("--dpi-scale="):
                result = arg.split("=")[1]
                return float(result)
        return 1.0

    @staticmethod
    def tryApplyDpiConfig():
        """尝试应用Dpi配置"""

        # enable dpi scale
        # note：开启自动高dpi支持，会导致其所保存的图片经过ocrmypdf转换为pdf时出现不明放大情况，
        # 因此推荐通过os.environ["QT_SCALE_FACTOR"]设置方式来设置Dpi
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
        return True

        # 如果采用了这种方式，pyinstaller打打包参数不能传入--onefile
        # 由于pyinstaller --onefile打包生成的.exe其临时解压文件夹名字是一样的，首次啥进程的时候
        # 自动删除%tmp%下的临时文件夹但此时又进行了一次程序重启行为，会导致该行为异常，
        # 因此不能使用--onefile参数
        # if "--debug" in sys.argv:
        #     os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        #     os.environ["QT_SCALE_FACTOR"] = "1.25"

        #     os.environ["debug"] = "1"

        #     return True
        # elif "--restarted" in sys.argv:
        #     scaleFactor = AppDpiHelper.extractDpiScale(sys.argv)
        #     os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        #     os.environ["QT_SCALE_FACTOR"] = f"{scaleFactor}"
        #     return True
        # else:
        #     AppDpiHelper.checkDpiAndRestartApplication()
        #     return False
