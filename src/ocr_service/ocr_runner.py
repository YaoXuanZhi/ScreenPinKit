import json
try:
    from paddleocr import PaddleOCR
    import paddleocr.tools.infer.utility as utility
    IsSupportOcr = True
except ImportError:
    IsSupportOcr = False

import numpy as np

class OcrService():
    def __init__(self) -> None:
        try:
            args = utility.parse_args()
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
        return IsSupportOcr

def main(args):
    if not OcrService.isSupported():
        print("OCR模块存在问题，已跳过")
        return    

    # 借用paddle默认的命令行参数
    imagePath = args.image_dir
    ocrService = OcrService()
    boxes, txts, scores = ocrService.ocr(imagePath)

    # 将ocr结果保存到json文件上
    jsonResult = {"boxes": [], "txts": [], "scores": []}
    jsonResult["boxes"] = json.dumps(boxes)
    jsonResult["txts"] = json.dumps(txts)

    # 假设这是你的包含float32类型的NumPy数组
    my_array = np.array(scores, dtype=np.float32)

    # 将NumPy数组转换为Python原生的list
    python_list = my_array.tolist()
    jsonResult["scores"] = json.dumps(python_list)

    # 将json文件保存到被识别图片的同级目录上
    jsonPath = f"{imagePath}.ocr"
    with open(jsonPath, 'w', encoding="utf-8") as f:
        json.dump(jsonResult, f, ensure_ascii=False, indent=4)

    print("已经完成了OCR识别")

if __name__ == '__main__':
    main(utility.parse_args())