#!/usr/bin/env python3
#Format: Pascal VOC: https://towardsdatascience.com/coco-data-format-for-object-detection-a4c5eaf518c5

# Jens Dede, Sustainable Communication Networks (ComNets)
# <jd@comnets.uni-bremen.de>
"""
Kind of a hacky script but seems to work. As usual: Needs a lot of refactoring.

Uses an arbitrary model to detect something on images (i.e. wolves), cuts out
the possible detections and stores the mapping between original image and
the cropped image. In theory, it should be possible to undo the mapping after
the subimages were analyzed by others.
"""

from pathlib import Path
import glob
import os
import sys
from PIL import Image
import json
import shutil

import datetime

import argparse
import glob

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.orm import sessionmaker

parser = argparse.ArgumentParser(description="Run image detection on the image, store the results into a db and cut the region of interest for additional processing")
parser.add_argument('sqlite', default="image-mapping.sqlite", type=str, help="The SQLITE-file with the mapping")
parser.add_argument('json', default="output.json", type=str, help="The json file from the app server")
parser.add_argument('--output_dir', default=None, help="The output dir for the images and database")
parser.add_argument('--min_percentage', default=0.6, help="The minimum voting to vote it as acceptable")
parser.add_argument('--ignore_higher', default=250, help="Ignore classes higher than this number")
parser.add_argument('--orig_images', default="orig-images", type=str, help="The directory with the original images")

args = parser.parse_args()

output_dir = args.output_dir

if not output_dir:
    output_dir = "output_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M_") + "to_label"
Path(output_dir).mkdir(parents=True, exist_ok=True)

engine = create_engine('sqlite:///'+args.sqlite)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class ImageMapping(Base):
    __tablename__ = "image_mapping"

    id = Column(Integer, primary_key=True)
    image_name    = Column(String)
    model_name    = Column(String)
    datetime      = Column(DateTime)
    subimage_name = Column(String)
    x_center_norm = Column(Float)
    y_center_norm = Column(Float)
    x_width_norm  = Column(Float)
    y_height_norm = Column(Float)
    class_numeric = Column(Integer)
    class_text    = Column(String)
    class_prop    = Column(Float)

    def __repr__(self):
        return f"<ImageMapping(image_name={self.image_name}, model_name={self.model_name}, datetime={self.datetime}, subimage_name={self.subimage_name}, x_center_norm={self.x_center_norm}, y_center_norm={self.y_center_norm}, x_width_norm={self.x_width_norm}, y_height_norm={self.y_height_norm}, class_numeric={self.class_numeric}, class_text={self.class_text}, class_prop={self.class_prop})>"
Base.metadata.create_all(engine)

votings = None
with open(args.json, "r") as j:
    votings = json.load(j)

complete_images = {}

with Session() as session:
    for image in votings["images"]:
        rel_votings = image["relative_class_voting"]
        max_voting = max(rel_votings, key=rel_votings.get)

        # Ignore unsure images
        if rel_votings[max_voting] < args.min_percentage:
            continue

        db_img = session.query(ImageMapping).filter(ImageMapping.subimage_name==image["image_name"]).all()
        if len(db_img) == 0:
            print("Unknown image. Skipping") # TODO: FIX
            continue
        if len(db_img) > 1:
            raise ValueError("Image mapping not distinct")

        # Create a dict of relevant images
        if db_img[0].image_name not in complete_images:
            complete_images[db_img[0].image_name] = {}
            group_images = session.query(ImageMapping).filter(ImageMapping.image_name==db_img[0].image_name).all()
            for gi in group_images:
                complete_images[db_img[0].image_name][gi.subimage_name] = {}

        # Fill the dict with the relevant information of the currently
        # processed image
        complete_images[db_img[0].image_name][db_img[0].subimage_name]["class"]  = max_voting
        complete_images[db_img[0].image_name][db_img[0].subimage_name]["voting"] = rel_votings[max_voting]


usable_images = []

for img in complete_images:
#    print(sum([0 if len(complete_images[img][subimg]) == 0 else 1 for subimg in complete_images[img]]), len(complete_images[img]))
#    print(complete_images[img])
    if sum([0 if len(complete_images[img][subimg]) == 0 else 1 for subimg in complete_images[img]]) == len(complete_images[img]):
        usable_images.append(img)
print(len(usable_images))


with Session() as session:
    for ui in usable_images:
        detection_rows = []
        original_image_file = glob.glob(os.path.join(args.orig_images, ui+"*"))

        if len(original_image_file) != 1:
            print("File not found or multiple options, skipping:", original_image_file)
            continue

        width, height = None, None

        with Image.open(original_image_file[0]) as im:
            width, height = im.size
        for subimage in complete_images[ui]:
            if int(complete_images[ui][subimage]["class"]) > args.ignore_higher:
                continue
            #print("Class from user voting", complete_images[ui][subimage]["class"])
            #print("Rating from user voting", complete_images[ui][subimage]["voting"])
            db_img = session.query(ImageMapping).filter(ImageMapping.subimage_name==subimage).all()[0]
            detection_rows.append(f"{int(complete_images[ui][subimage]['class'])} {db_img.x_center_norm} {db_img.y_center_norm} {db_img.x_width_norm} {db_img.y_height_norm}")

        shutil.copy(original_image_file[0], output_dir)
        with open(os.path.join(output_dir, ui+".txt"), "w") as f:
            f.writelines("\n".join(detection_rows))


with open(os.path.join(output_dir, "classes.txt"), "w") as f:
    for cls in votings["classes"]:
        f.writelines(f"{cls['class_id']} {cls['class_name']}\n")
