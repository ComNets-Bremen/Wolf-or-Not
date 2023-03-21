#!/usr/bin/env python3

# Jens Dede, Sustainable Communication Networks (ComNets)
# <jd@comnets.uni-bremen.de>
"""
Comparison of the original detections (sqlite) and the user votes from the app (json)
"""

from pathlib import Path
import glob
import os
import sys
from PIL import Image
import json

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

import datetime

import argparse
import glob

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.orm import sessionmaker

parser = argparse.ArgumentParser(description="How much do the user detection differ from the the original images? -> This script gives the answer.")
parser.add_argument('sqlite', default="image-mapping.sqlite", type=str, help="The SQLITE-file with the mapping")
parser.add_argument('json', default="output.json", type=str, help="The json file from the app server")
args = parser.parse_args()

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

correct_classes_props = []
wrong_classes_props = []

with Session() as session:
    for image in votings["images"]:
        rel_votings = image["relative_class_voting"]
        max_voting = max(rel_votings, key=rel_votings.get)

        db_img = session.query(ImageMapping).filter(ImageMapping.subimage_name==image["image_name"]).all()
        if len(db_img) == 0:
            print("Unknown image. Skipping") # TODO: FIX
            continue
        if len(db_img) > 1:
            raise ValueError("Image mapping not distinct")


        app_prop  = rel_votings[max_voting]
        app_class = int(max_voting)
        model_class_num = db_img[0].class_numeric
        model_prop = db_img[0].class_prop
        if app_class == model_class_num:
            correct_classes_props.append(model_prop)
        else:
            wrong_classes_props.append(model_prop)

        print(image["image_name"], "model predicted", model_class_num, "with prop", model_prop, "and app got class", app_class, "with prop", app_prop)


total_images = len(correct_classes_props) + len(wrong_classes_props)
print(f"Correct percentage: {len(correct_classes_props)/total_images}")
print(f"Wrong percentage: {len(wrong_classes_props)/total_images}")


print("Wrong props:")
print(f"median: {np.median(wrong_classes_props)}, mean: {np.mean(wrong_classes_props)}, stddev: {np.std(wrong_classes_props)}")
print("Correct props:")
print(f"median: {np.median(correct_classes_props)}, mean: {np.mean(correct_classes_props)}, stddev: {np.std(correct_classes_props)}")

bins = np.linspace(0, 1, 100)

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "sans-serif",
})

fig, ax = plt.subplots(figsize=(5, 3))
ax.hist(wrong_classes_props, bins, density=1, label="Wrong", alpha=0.5, color="red")
ax.hist(correct_classes_props, bins, density=1, label="Correct", alpha=0.5, color="green")
ax.xaxis.set_major_formatter(mtick.PercentFormatter(1))
ax.set_yticklabels([])
ax.set_xlabel(f"Scores (probabilities of detection), n={total_images}")
ax.set_ylabel("Normalized Frequency")
plt.legend(loc='upper left')
plt.title("Comparison of Model Predictions and User Votes")
fig.tight_layout()
plt.savefig("dist.pdf")
plt.show()


