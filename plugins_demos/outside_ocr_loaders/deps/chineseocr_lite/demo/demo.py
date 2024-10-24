import os, sys, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from model import  OcrHandle
from PIL import Image, ImageDraw,ImageFont

ocrhandle = OcrHandle()

def main(args):
    input_path = args.input_path
    output_path = args.output_path
    dpi_scale = args.dpi_scale
    imgPath = input_path
    img = Image.open(imgPath)
    img = img.convert("RGB")

    short_size = 960
    res = ocrhandle.text_predict(img,short_size)

    img_detected = img.copy()
    img_draw = ImageDraw.Draw(img_detected)
    colors = ['red', 'green', 'blue', "purple"]

    for i, r in enumerate(res):
        rect, txt, confidence = r

        x1,y1,x2,y2,x3,y3,x4,y4 = rect.reshape(-1)
        size = max(min(x2-x1,y3-y2) // 2 , 20 )

        myfont = ImageFont.truetype(os.path.join(os.getcwd(), "仿宋_GB2312.ttf"), size=size)
        fillcolor = colors[i % len(colors)]
        img_draw.text((x1, y1 - size ), str(i+1), font=myfont, fill=fillcolor)
        for xy in [(x1, y1, x2, y2), (x2, y2, x3, y3 ), (x3 , y3 , x4, y4), (x4, y4, x1, y1)]:
            img_draw.line(xy=xy, fill=colors[i % len(colors)], width=2)

    img_detected.save(output_path)

    print(res)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", type=str)
    parser.add_argument("--output_path", type=str)
    parser.add_argument("--dpi_scale", type=float)

    return parser.parse_args()

if __name__ == "__main__":
    main(parse_args())