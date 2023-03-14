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
import torch
from PIL import Image

import datetime

import argparse
import glob

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.orm import sessionmaker

parser = argparse.ArgumentParser(description="Run image detection on the image, store the results into a db and cut the region of interest for additional processing")
parser.add_argument("model", type=str, help="The model to be used.")
parser.add_argument("images", type=str, nargs="+", help="The images as an array")
parser.add_argument('--glob', action='store_true', help="interpret string as glob")
parser.add_argument('--export_labels', action='store_true', help="Store current detections in YOLO-Format next to the images")
parser.add_argument('--batchsize', default=5, help="Batchsize for image processing")
parser.add_argument('--force-reload', action='store_true', help="Force reloading the model")
parser.add_argument('--output_dir', default=None, help="The output dir for the images and database")

args = parser.parse_args()

output_dir = args.output_dir

safe_model_name = "".join([c for c in os.path.basename(args.model).replace(".", "_") if c.isalpha() or c.isdigit() or c in [" ", "_"]]).rstrip()

if not output_dir:
    output_dir = "output_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M_") + safe_model_name
Path(output_dir).mkdir(parents=True, exist_ok=True)

images_list = args.images

if args.glob:
    if len(args.images) != 1:
        print("Glob works only with a single argument")
    images_list = glob.glob(args.images[0])


engine = create_engine('sqlite:///'+os.path.join(output_dir, "image-mapping.sqlite"))
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


def batch(iterable, n=args.batchsize):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

model = torch.hub.load('ultralytics/yolov5', 'custom', args.model, force_reload=args.force_reload)

# use model.eval, torch.go_grad()??

for i in batch(images_list):
    print("Eval", i)
    results = model(i)
    classes = results.names
    print(classes)
    for image in zip(i, results.xyxy):
        img_path = image[0]
        img_dir = os.path.dirname(img_path)
        txt_path = os.path.join(img_dir, Path(image[0]).stem + ".txt")
        classes_path = os.path.join(img_dir, "classes.txt")
        with Image.open(image[0]) as im:
            width, height = im.size
            if len(image[1]):
                # xmin    ymin    xmax   ymax  confidence  class
                export_rows = None
                if args.export_labels:
                    export_rows = []
                for cnt, detection in enumerate(image[1].tolist()):
                    print(detection)
                    cls = int(detection[-1])
                    x_center = detection[0] + ((detection[2] - detection[0])/2)
                    y_center = detection[1] + ((detection[3] - detection[1])/2)
                    d_width = detection[2] - detection[0]
                    d_height = detection[3] - detection[1]
                    # normalize

                    x_center = x_center / width
                    y_center = y_center / height
                    d_width = d_width / width
                    d_height = d_height / height

                    subimage = im.crop((detection[0], detection[1], detection[2], detection[3]))
                    output_filename = Path(image[0]).stem + f"_subimg_{cnt}.jpg"
                    subimage.save(os.path.join(output_dir, output_filename))

                    with Session() as session:
                        db_image_mapping = ImageMapping(
                                image_name = Path(image[0]).stem,
                                model_name = safe_model_name,
                                datetime   = datetime.datetime.now(),
                                subimage_name = output_filename,
                                x_center_norm = x_center,
                                y_center_norm = y_center,
                                x_width_norm = d_width,
                                y_height_norm = d_height,
                                class_numeric = cls,
                                class_text = classes[cls],
                                class_prop = detection[-2]
                                )
                        session.add(db_image_mapping)
                        session.commit()


                    if export_rows:
                        export_rows.append(f"{cls} {x_center} {y_center} {d_width} {d_height}")
                        with open(txt_path, "w") as f:
                            f.writelines("\n".join(export_rows))

                        if not os.path.isfile(classes_path):
                            with open(classes_path, "w") as f:
                                for i in classes:
                                    f.writelines(f"{i} {classes[i]}\n")
    print(10*"#")
