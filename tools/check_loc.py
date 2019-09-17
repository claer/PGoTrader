#!/usr/bin/env python3.7

import argparse

import yaml
from PIL import Image
import sys
from pyocr import pyocr
from pyocr import builders

debuglvl=None

with open("../config.yaml", "r") as f:
    config = yaml.load(f)

tools = pyocr.get_available_tools()
tool = tools[0]

def ocr_img(img, loc, debug=None):
    image=Image.open(img)
    crop=image.crop(loc)
    if debug != None:
        crop.show()
    print(tool.image_to_string(crop).replace("\n", " "))

# usage '__name__' --loc location --app app1|app2 image

def main():
    parser = argparse.ArgumentParser(description='Pokemon GO image tester')
    parser.add_argument('--loc', type=str, default=None,
                        help="Crop location from config file")
    parser.add_argument('--app', default='app1', type=str,
                        help='App to capture: app1|app2')
    parser.add_argument('imagefile', help='Image file to parse')
    args = parser.parse_args()

    if args.loc == None:
        print('location needed. Exiting')
        sys.exit(0)

    print('Checking {} on {}'.format(args.loc, args.app))
    ocr_img(args.imagefile, config[args.app]['locations'][args.loc], debug=debuglvl)

if __name__ == "__main__":
    main()

