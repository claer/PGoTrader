#!/usr/bin/env python3.7
import sys
import argparse

import yaml
from PIL import Image
from pyocr import pyocr
from pyocr import builders


with open("../config.yaml", "r") as f:
    config = yaml.safe_load(f)

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
    parser.add_argument('--debug', help='Debug level, default None', default=None)
    parser.add_argument('imagefile', help='Image file to parse')
    args = parser.parse_args()

    debuglvl=args.debug

    if args.loc == None:
        print('location needed. Exiting')
        sys.exit(0)

    print('location: {}'.format(str(config[args.app]['locations'][args.loc])))

    print('Checking {} on {}'.format(args.loc, args.app))
    ocr_img(args.imagefile, config[args.app]['locations'][args.loc], debug=debuglvl)

if __name__ == "__main__":
    main()

