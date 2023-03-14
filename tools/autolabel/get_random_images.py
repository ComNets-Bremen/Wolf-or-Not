#!/usr/bin/env python3

# Jens Dede, Sustainable Communication Networks (ComNets)
# <jd@comnets.uni-bremen.de>
"""
Get a random set of images from a given directory
"""

from pathlib import Path
import os
import sys
import random
import datetime
import shutil

import argparse
import glob

parser = argparse.ArgumentParser(description="Randomly get a certain number of images from a given directory")
parser.add_argument("input_dir", type=str, help="The input image directory")
parser.add_argument('--output_dir', '-o', default=None, help="The output image directory")
parser.add_argument('--number', '-n', default=2000, type=int, help="Number of images to be taken randomly")
parser.add_argument('--extension', '-e', default="jpg", type=str, help="The fileextension of the images")

args = parser.parse_args()

output_dir = args.output_dir

if not output_dir:
    output_dir = "output_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
Path(output_dir).mkdir(parents=True, exist_ok=True)

images_list = glob.glob(os.path.join(args.input_dir, "*."+args.extension))

if len(images_list) <= args.number:
    raise ValueError("Number images in directory is smaller than required amount of images. Aborting")

for image in random.sample(images_list, args.number):
    shutil.copy(image, output_dir)

