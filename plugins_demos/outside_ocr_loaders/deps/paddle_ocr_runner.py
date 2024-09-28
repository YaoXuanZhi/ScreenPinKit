import json
import argparse
try:
    from paddleocr import PaddleOCR
    _isSupportOcr = True
except ImportError:
    _isSupportOcr = False

import numpy as np

class OcrService():
    def __init__(self, args) -> None:
        try:
            self.ocrModel = PaddleOCR(
                det_model_dir=args.det_model_dir, 
                rec_model_dir=args.rec_model_dir, 
                cls_model_dir=args.cls_model_dir, 
                rec_char_dict_path=args.rec_char_dict_path,
                use_angle_cls=True
                )
        except Exception:
            self.ocrModel = None

    def ocr(self, imagePath):
        if self.ocrModel == None:
            return [], [], []
        result = self.ocrModel.ocr(imagePath, cls=True)
        boxes = [line[0] for line in result]
        txts = [line[1][0] for line in result]
        scores = [line[1][1] for line in result]
        return boxes, txts, scores

    @staticmethod
    def isSupported():
        return _isSupportOcr

def main(args):
    if not OcrService.isSupported():
        print("OCR模块存在问题，已跳过")
        return    

    # 借用paddle默认的命令行参数
    input = args.input_path
    output = args.output_path
    ocrService = OcrService(args)
    boxes, txts, scores = ocrService.ocr(input)

    # 将ocr结果保存到json文件上
    jsonResult = {"boxes": [], "txts": [], "scores": []}
    # box = [[leftTop] [rightTop] [rightBottom] [leftBottom]]
    jsonResult["boxes"] = json.dumps(boxes)
    jsonResult["txts"] = json.dumps(txts)

    # 假设这是你的包含float32类型的NumPy数组
    my_array = np.array(scores, dtype=np.float32)

    # 将NumPy数组转换为Python原生的list
    python_list = my_array.tolist()
    jsonResult["scores"] = json.dumps(python_list)

    # 将json文件保存到被识别图片的同级目录上
    with open(output, 'w', encoding="utf-8") as f:
        json.dump(jsonResult, f, ensure_ascii=False, indent=4)

    print("已经完成了OCR识别")

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

    return parser.parse_args()

if __name__ == "__main__":
    main(parse_args())