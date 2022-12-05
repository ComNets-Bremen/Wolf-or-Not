#!/usr/bin/env python3

import json
import os
from pathlib import Path
import requests
from requests.exceptions import SSLError
import shutil
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-o", "--out", type=str, default="out", help="The data output directory")
ap.add_argument("json", help="The json file to open")
ap.add_argument("--token", default=None, help="Token to download high res images")

args = vars(ap.parse_args())

isHttps = True

json_data = None

def getClassName(class_id, class_list):
    for c in class_list:
        if int(class_id) == c["class_id"]:
            return c["class_name"]

    return "class_"+str(class_id)


with open(args["json"]) as jf:
    json_data = json.load(jf)

token = None
if args["token"]:
    token = args["token"]

for image in json_data["images"]:
    rcv = image["relative_class_voting"]
    relevant_class = max(rcv, key=rcv.get)
    if rcv[relevant_class] < 0.8:
        print("Voting not sure enough, skipping", rcv)
        continue

    outdir = os.path.join(args["out"], getClassName(relevant_class, json_data["classes"]))
    Path(outdir).mkdir(parents=True, exist_ok=True)

    img_filename = image["image_name"]

    if os.path.exists(os.path.join(outdir, img_filename)):
        print("Skipping download: File already exists")
        continue

    headers = {}
    url = image["image_url"]

    if token:
        url = image["image_url"].replace("/img/", "/original-img/")
        headers = {'Authorization': 'Token ' + str(token)}

    res = None

    if isHttps:
        try:
            res = requests.get("https://" + url, stream=True, headers=headers)
        except SSLError:
            isHttps = False
            res = requests.get("http://" + url, stream=True, headers=headers)
    else: # no https
        res = requests.get("http://" + url, stream=True, headers=headers)

    if res.status_code == 200:
        with open(os.path.join(outdir, img_filename),'wb') as f:
            shutil.copyfileobj(res.raw, f)
            print('Image sucessfully Downloaded: ', img_filename)
    elif 400 <= res.status_code < 500:
        print("Invalid authentication. Please check your request. Error code: " + str(res.status_code))
        break
    else:
        print('Image Couldn\'t be retrieved. Status code: ' + str(res.status_code) )

#    res = requests.get(url, stream = True)






