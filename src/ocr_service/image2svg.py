import os, math
import argparse
from paddleocr import PaddleOCR
from PIL import Image, ImageFont
import html

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

    def calculate_best_font_size(text, font_path, max_width, max_height, initial_font_size=5):
        """
        计算最适合固定文本框的字体大小
        :param text: 要显示的文本
        :param font_path: 字体文件路径
        :param max_width: 文本框的最大宽度
        :param max_height: 文本框的最大高度
        :param initial_font_size: 初始字体大小
        :return: 最适合的字体大小
        """

        font_size = initial_font_size

        while True:
            font = ImageFont.truetype(font_path, font_size)
            text_width, text_height = font.getsize(text)

            if text_width <= max_width and text_height <= max_height:
                font_size += 1
            else:
                font_size -= 1
                break

        return font_size

    # 构建 HTML 内容
    html_content = f"""
<svg width="100%" height="100%" viewBox="0 0 {width} {height}" preserveAspectRatio="xMaxYMax slice" xmlns="http://www.w3.org/2000/svg">
    """

    # 遍历 OCR 结果，生成 HTML 文本层
    for line in result:
        (box, word) = line
        text, _ = word
        left_top, right_top, right_bottom, left_bottom = box
        x, y = left_top
        w = right_top[0] - left_top[0]
        h = left_bottom[-1] - left_top[-1]

        best_font_size = calculate_best_font_size(text, "arial.ttf", w, h, 2)

        x = x / dpi_scale
        y = y / dpi_scale
        w = w / dpi_scale
        h = h / dpi_scale
        text = html.escape(text)

        html_content += f"""
    <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="gray"/>
    <text x="{x}" y="{y+h}" width="{w}" height="{h}" font-family="Arial" font-size="{best_font_size}" fill="blue" textLength="{w}" lengthAdjust="spacingAndGlyphs">
        {text}
    </text>
        """

    html_content += """
</svg>
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

    image_path = args.image_path
    svg_path = args.svg_path
    dpi_scale = args.dpi_scale
    image_to_html(ocr, image_path, svg_path, dpi_scale)

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

    parser.add_argument("--image_path", type=str)
    parser.add_argument("--svg_path", type=str)
    parser.add_argument("--dpi_scale", type=float)

    return parser.parse_args()

if __name__ == "__main__":
    main(parse_args())