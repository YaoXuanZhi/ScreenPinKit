import os, math, argparse, html
from paddleocr import PaddleOCR
from PIL import Image

def image_to_html(ocr, input, output, dpi_scale=1):
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

            /* 禁止所有元素被选择 */
            * {{
                -webkit-user-select: none; /* 适用于WebKit浏览器（如Chrome、Safari） */
                -moz-user-select: none; /* 适用于Firefox */
                -ms-user-select: none; /* 适用于IE10+ */
                user-select: none; /* 标准属性 */
            }}

            /* 允许文本被选择 */
            p, span, div {{
                -webkit-user-select: text; /* 适用于WebKit浏览器（如Chrome、Safari） */
                -moz-user-select: text; /* 适用于Firefox */
                -ms-user-select: text; /* 适用于IE10+ */
                user-select: text; /* 标准属性 */
            }}

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
                opacity: 0
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
                background-color: rgba(64, 128, 191, 0.5);
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

            // 监听 keydown 事件
            document.addEventListener('keydown', function(event) {{
                if (event.ctrlKey && event.key === 'c') {{
                    //由于WebEngineView的复制结果并不符合预期，因此屏蔽掉再额外做处理
                    event.preventDefault();
                    // 透传网页的复制事件
                    window.receiver.hookCopyText(window.getSelection().toString());
                }}
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
        text = html.escape(text)

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
    ocr = PaddleOCR(
            det_model_dir=args.det_model_dir, 
            rec_model_dir=args.rec_model_dir, 
            cls_model_dir=args.cls_model_dir, 
            rec_char_dict_path=args.rec_char_dict_path,
            use_angle_cls=True
            )

    input_path = args.input_path
    output_path = args.output_path
    dpi_scale = args.dpi_scale
    image_to_html(ocr, input_path, output_path, dpi_scale)

def parse_args():
    def str2bool(v):
        return v.lower() in ("true", "t", "1")

    parser = argparse.ArgumentParser()
    # params for prediction engine
    parser.add_argument("--use_gpu", type=str2bool, default=True)
    parser.add_argument("--ir_optim", type=str2bool, default=True)
    parser.add_argument("--use_tensorrt", type=str2bool, default=False)
    parser.add_argument("--use_fp16", type=str2bool, default=False)
    parser.add_argument("--gpu_mem", type=int, default=500)

    # params for text detector
    parser.add_argument("--det_algorithm", type=str, default='DB')
    parser.add_argument("--det_model_dir", type=str)
    parser.add_argument("--det_limit_side_len", type=float, default=960)
    parser.add_argument("--det_limit_type", type=str, default='max')

    # DB parmas
    parser.add_argument("--det_db_thresh", type=float, default=0.3)
    parser.add_argument("--det_db_box_thresh", type=float, default=0.5)
    parser.add_argument("--det_db_unclip_ratio", type=float, default=1.6)
    parser.add_argument("--max_batch_size", type=int, default=10)
    parser.add_argument("--use_dilation", type=bool, default=False)

    # EAST parmas
    parser.add_argument("--det_east_score_thresh", type=float, default=0.8)
    parser.add_argument("--det_east_cover_thresh", type=float, default=0.1)
    parser.add_argument("--det_east_nms_thresh", type=float, default=0.2)

    # SAST parmas
    parser.add_argument("--det_sast_score_thresh", type=float, default=0.5)
    parser.add_argument("--det_sast_nms_thresh", type=float, default=0.2)
    parser.add_argument("--det_sast_polygon", type=bool, default=False)

    # params for text recognizer
    parser.add_argument("--rec_algorithm", type=str, default='CRNN')
    parser.add_argument("--rec_model_dir", type=str)
    parser.add_argument("--rec_image_shape", type=str, default="3, 32, 320")
    parser.add_argument("--rec_char_type", type=str, default='ch')
    parser.add_argument("--rec_batch_num", type=int, default=6)
    parser.add_argument("--max_text_length", type=int, default=25)
    parser.add_argument(
        "--rec_char_dict_path",
        type=str,
        default="./ppocr/utils/ppocr_keys_v1.txt")
    parser.add_argument("--use_space_char", type=str2bool, default=True)
    parser.add_argument(
        "--vis_font_path", type=str, default="./doc/fonts/simfang.ttf")
    parser.add_argument("--drop_score", type=float, default=0.5)

    # params for text classifier
    parser.add_argument("--use_angle_cls", type=str2bool, default=False)
    parser.add_argument("--cls_model_dir", type=str)
    parser.add_argument("--cls_image_shape", type=str, default="3, 48, 192")
    parser.add_argument("--label_list", type=list, default=['0', '180'])
    parser.add_argument("--cls_batch_num", type=int, default=6)
    parser.add_argument("--cls_thresh", type=float, default=0.9)

    parser.add_argument("--enable_mkldnn", type=str2bool, default=False)
    parser.add_argument("--use_pdserving", type=str2bool, default=False)

    parser.add_argument("--input_path", type=str)
    parser.add_argument("--output_path", type=str)
    parser.add_argument("--dpi_scale", type=float)

    return parser.parse_args()

if __name__ == "__main__":
    main(parse_args())