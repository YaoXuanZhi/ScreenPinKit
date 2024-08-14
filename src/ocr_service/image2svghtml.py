import os, math, argparse, html
from paddleocr import PaddleOCR
from PIL import Image, ImageFont
from html_builder import image_to_svg_html as build_svg_html

def image_to_html(ocr, input, output, dpi_scale=1):
    '''将图片进行OCR识别后，将结果转换成html'''
    # 打开图片
    image = Image.open(input)

    # 获取图片的宽度和高度
    width, height = image.size

    # 使用 PaddleOCR 进行 OCR 识别
    result = ocr.ocr(input, cls=True)

    boxes = []
    txts = []

    # 遍历 OCR 结果，生成 HTML 文本层
    for line in result:
        (box, word) = line
        text, _ = word
        left_top, right_top, right_bottom, left_bottom = box
        boxes.append([left_top, right_top, right_bottom, left_bottom])
        txts.append(text)

    html_content = build_svg_html(width=width, height=height, boxes=boxes, txts=txts, dpi_scale=dpi_scale)
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