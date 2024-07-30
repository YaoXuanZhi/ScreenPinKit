import os, math
from paddleocr import PaddleOCR
import paddleocr.tools.infer.utility as utility
from PIL import Image
import numpy as np

def image_to_html(ocr, input, output, dpi_scale=1.25):
    '''将图片进行OCR识别后，将结果转换成html'''
    # 打开图片
    image = Image.open(input)

    # 获取图片的宽度和高度
    width, height = image.size
    width = width / dpi_scale
    height = height / dpi_scale

    # 使用 PaddleOCR 进行 OCR 识别
    result = ocr.ocr(input, cls=True)

    # 构建 HTML 内容
    html_content = f"""
    <html>
    <head>
        <title>OCR Result</title>
        <style>
            body {{
                background-color: transparent;
                margin: 0;
                padding: 0;
                box-sizing: border-box; /* 确保内边距和边框不会增加元素的宽度 */
            }} 

            ::selection{{
                background-color: transparent;
            }}

            .ocr_image {{
                position: relative;
                width: {width}px;
                height: {height}px;
            }}

            img {{
                width: 100%;
                height: 100%;
                pointer-events: none; /* 禁止鼠标事件 */
            }}

            .container {{
                position: absolute;
                white-space: pre;
                /* border: 1px solid gray; */
                background-color: transparent;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden; /* 防止内容溢出 */
            }}

            .text {{
                font-family: Arial, sans-serif;
                font-size: 5px; /* 初始字体大小 */
                line-height: 1.2; /* 初始行高 */
                display: inline-block;
                /* color: red; */
                color: transparent;
                max-width: 100%;
                max-height: 100%;
                overflow: hidden;
                /* text-overflow: ellipsis; */
                white-space: nowrap; /* 防止文本换行 */
                text-align: justify;
            }}

            .text::selection {{
                color: transparent;
                background-color: rgba(20, 30, 55, 0.2);
            }}

            /* 使用媒体查询或JavaScript动态调整字体大小和行距 */
            @media (max-width: 400px) {{
                .text {{
                    font-size: 14px;
                    line-height: 1.1;
                }}
            }}

            @media (max-width: 300px) {{
                .text {{
                    font-size: 12px;
                    line-height: 1.0;
                }}
            }}

            /* 隐藏所有滚动条 */
            :root {{
            overflow: hidden;
            /* background-color: orange; */
            background-color: transparent;
            }}
        </style>

        <script src="qrc:/qtwebchannel/qwebchannel.js"></script>
        <script>
            // 屏蔽右键菜单
            document.addEventListener('contextmenu', function(event) {{
                event.preventDefault();
            }});

            // 初始化QWebChannel
            new QWebChannel(qt.webChannelTransport, function(channel) {{
                window.receiver = channel.objects.receiver;
                window.receiver.htmlRenderFinished(document.documentElement.scrollWidth, document.documentElement.scrollHeight);
            }});
        </script>

        <script>
                function adjustFontSize() {{
                    // 获取所有具有特定类名的元素
                    const elements = document.querySelectorAll('.container');

                    // 遍历所有元素
                    elements.forEach((element, index) => {{
                        const container = element;
                        const text = container.querySelector('.text');
                        const containerWidth = container.clientWidth;
                        const containerHeight = container.clientHeight;

                        let fontSize = 2; // 初始字体大小
                        let lineHeight = 1.2; // 初始行高

                        // 调整字体大小，直到文本适应容器
                        while (text.scrollWidth <= containerWidth && text.scrollHeight <= containerHeight) {{
                            fontSize += 0.5;
                            text.style.fontSize = fontSize + 'px';
                            text.style.lineHeight = lineHeight;
                        }}

                        let textWidth = text.scrollWidth
                        if (textWidth < containerWidth) {{
                            // 计算需要的字符间距
                            const excessWidth = containerWidth - textWidth;
                            const numChars = text.textContent.length;
                            const letterSpacing = excessWidth / numChars;

                            // 设置字符间距
                            text.style.letterSpacing = `${{letterSpacing}}px`;
                        }} else {{
                            // 如果文本宽度小于或等于容器宽度，移除字符间距
                            text.style.letterSpacing = '0px';
                        }}
                    }});
                }}

            // 页面加载时调整字体大小
            window.addEventListener('load', adjustFontSize);

            // 窗口大小改变时重新调整字体大小
            window.addEventListener('resize', adjustFontSize);
        </script>
    </head>
    <body class="ocr_image">
        <img src="{os.path.basename(input)}">
    """

    # 遍历 OCR 结果，生成 HTML 文本层
    for line in result:
        (box, word) = line
        text, _ = word
        left_top, right_top, right_bottom, left_bottom = box
        x, y = left_top
        w = right_top[0] - left_top[0]
        h = left_bottom[-1] - left_top[-1]

        x = x / dpi_scale
        y = y / dpi_scale
        w = w / dpi_scale
        h = h / dpi_scale

        html_content += f"""
        <div class="container" style="left: {x}px; top: {y}px; width: {w}px; height: {h}px;">
            <span class="text">{text}</span>
        </div>
        """

    html_content += """
    </body>
    </html>
    """

    with open(output, 'w', encoding='utf-8') as f:
        f.write(html_content)

def main(args):
    # 初始化 PaddleOCR
    args = utility.parse_args()
    ocr = PaddleOCR(
            det_model_dir=args.det_model_dir, 
            rec_model_dir=args.rec_model_dir, 
            cls_model_dir=args.cls_model_dir, 
            rec_char_dict_path=args.rec_char_dict_path,
            use_angle_cls=True
            )

    input = args.image_dir
    image_to_html(ocr, input, f"{input}.html")

if __name__ == "__main__":
    main(utility.parse_args())