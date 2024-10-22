import sys, os, json, argparse
from PIL import Image
import pytesseract
from lxml import etree
import numpy as np

import sys, os
sys.path.insert(0, os.path.join( os.path.dirname(__file__), "..", ".." ))

def main(args):
    input_path = args.input_path
    output_path = args.output_path

    # 设置 Tesseract-OCR 的路径（仅在 Windows 上需要）
    pytesseract.pytesseract.tesseract_cmd = r'tesseract.exe'

    # 打开图像文件
    image = Image.open(input_path)

    infos = pytesseract.image_to_alto_xml(image, lang='chi_sim')

    xml_path = f"{input_path}.xml"
    with open(xml_path, 'wb') as f:
        f.write(infos)

    tree = etree.parse(xml_path)
    root = tree.getroot()

    # 定义命名空间
    namespace = {'alto': 'http://www.loc.gov/standards/alto/ns-v3#'}

    # 遍历 TextLine 标签
    data = []
    for text_line in root.findall('.//alto:TextLine', namespace): 
        text = ""
        # 遍历 TextLine 的子标签下的所有String标签
        for child in text_line:
            if child.tag.endswith('String'):
                text = text + child.attrib.get('CONTENT')

        left = float(text_line.get('HPOS'))
        top = float(text_line.get('VPOS'))
        width = float(text_line.get('WIDTH'))
        height = float(text_line.get('HEIGHT'))

        left_top = [left, top]
        right_top = [left + width, top]
        right_bottom = [left + width, top + height]
        left_bottom = [left, top + height]
        score = 0.97
        box = [left_top, right_top, right_bottom, left_bottom]
        data.append({"box": box, "text": text, "score": score})

    jsonResult = {"code" : 100, "data" : data}

    # 将json文件保存到被识别图片的同级目录上
    with open(output_path, 'w', encoding="utf-8") as f:
        json.dump(jsonResult, f, ensure_ascii=False, indent=4)

    print("已经完成了OCR识别")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", type=str)
    parser.add_argument("--output_path", type=str)
    return parser.parse_args()

if __name__ == "__main__":
    main(parse_args())