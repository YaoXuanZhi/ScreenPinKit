<p align="center">
  <img width="18%" align="center" src="https://raw.githubusercontent.com/YaoXuanZhi/ScreenPinKit/main/images/logo.svg" alt="logo">
</p>
  <h1 align="center">
  ScreenPinKit
</h1>
<p align="center">
  一款基于PyQt5的迷你截图标注、桌面标注工具
</p>

<p align="center">
  <a href="https://pypi.org/project/ScreenPinKit" target="_blank">
    <img src="https://img.shields.io/pypi/v/ScreenPinKit?color=%2334D058&label=Version" alt="Version">
  </a>

  <a style="text-decoration:none">
    <img src="https://static.pepy.tech/personalized-badge/pyqt-fluent-widgets?period=total&units=international_system&left_color=grey&right_color=brightgreen&left_text=Downloads" alt="Download"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/License-GPLv3-blue?color=#4ec820" alt="GPLv3"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/Platform-Win32%20-blue?color=#4ec820" alt="Platform Win32"/>
  </a>
</p>

<p align="center">
<a href="../README.md">English</a> | 简体中文
</p>

![Interface](https://raw.githubusercontent.com/YaoXuanZhi/ScreenPinKit/main/images/Interface.png)

![OCR](https://raw.githubusercontent.com/YaoXuanZhi/ScreenPinKit/main/images/ocr.png)

## 安装
```shell
# 暂时只推荐在Python3.8、Python3.9上安装
## 源码安装
#cd src/
#python setup.py install
# pip安装
pip install ScreenPinKit -i https://pypi.org/simple/

ScreenPinKit
```

> **Warning**
> 该应用使用了第三方库system_hotkey来注册全局快捷键，但是由于该包已经有3年以上不维护了，推荐在python3.8上安装并运行

## 运行示例
使用 pip 安装好 ScreenPinKit 包并下载好此仓库的代码之后，就可以运行 src 目录下的任意示例程序，比如：

```sh
cd src
python main.py

python ./canvas_editor/demos/canvas_editor_demo_full.py

python ./canvas_item/demos/canvas_arrow_demo.py

```

## 打包单文件
```sh
# Windows Defender可能会报毒，忽略即可打包出来
pyinstaller --onefile --icon=../images/logo.png --windowed main.py -n ScreenPinKit
```

## 使用教程
| 作用域 | 快捷键 | 作用 |
|-------|-------|-------|
| 全局 | F7 | 截图 |
| 全局 | F4 | 呼出屏幕标注 |
| 全局 | F2 | 在鼠标位置上显示剪贴板上的图像 |
| 全局 | Esc | 逐步退出该窗口的编辑状态 |
| 截图窗口 | Ctrl+T | 将截图选区转换为屏幕贴图 |
| 截图窗口 | Shift | 切换放大镜上的颜色格式(rgb/hex) |
| 截图窗口 | C | 复制当前拾取到的颜色格式 |
| 贴图窗口 | Ctrl+A | OCR识别 |
| 贴图窗口 | Alt+F | 切换鼠标穿透状态 |
| 贴图窗口 | Ctrl+C | 复制当前贴图到剪贴板上 |
| 贴图窗口 | Ctrl+S | 将当前贴图保存到磁盘上 |
| 贴图窗口 | Ctrl+W | 完成绘图 |
| 屏幕标注窗口 | Alt+L | 隐藏/显示屏幕标注内容 |
| 屏幕标注窗口 | Ctrl+W | 完成绘图 |

请仔细阅读 [wiki](https://github.com/YaoXuanZhi/ScreenPinKit/wiki)

## 参考
* [**Snipaste**: Snipaste 是一个简单但强大的截图工具，也可以让你将截图贴回到屏幕上](https://zh.snipaste.com/)
* [**excalidraw**: Design guidelines and toolkits for creating native app experiences](https://excalidraw.com/)
* [**PyQt-Fluent-Widgets**: A fluent design widgets library based on C++ Qt/PyQt/PySide. Make Qt Great Again.](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)
* [**ShareX**: Screen capture, file sharing and productivity tool](https://github.com/ShareX/ShareX)
* [**ppInk**: An easy to use on-screen annotation software inspired by Epic Pen.](https://github.com/onyet/ppInk/)
* [**pyqtgraph**: Fast data visualization and GUI tools for scientific / engineering applications](https://github.com/pyqtgraph/pyqtgraph)
* [**Jamscreenshot**: 一个用python实现的类似微信QQ截屏的工具源码，整合提取自本人自制工具集Jamtools](https://github.com/fandesfyf/Jamscreenshot)
* [**EasyCanvas**: 基于Qt QGraphicsView的简易画图软件](https://github.com/douzhongqiang/EasyCanvas)
* [**PixPin**: 功能强大使用简单的截图/贴图工具，帮助你提高效率](https://pixpinapp.com/)

<details>
<summary>TodoList</summary>

 - ☐ 修复system_hotkey的异常表现
   >经测试，在python3.10下会抛异常，并且在python3.8上其异常也不能被正常捕获，考虑到它已经有将近3年不维护了，需要做对它做全方位的兼容性处理
 - ☐ 无感设置快捷键
 - ☐ 无感切换语言
 - ☐ 插件市场
   - ✔ 添加插件系统
   - ☐ 添加插件市场UI
 - ✔ 更快的离线OCR识别支持
 - ✔ 完善OCR识别层的UI显示

</details>