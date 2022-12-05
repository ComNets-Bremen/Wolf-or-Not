#!/usr/bin/env python3
"""
Jens Dede, ComNets, Uni Bremen, 2022
jd@comnets.uni-bremen.de


Image preprocessing tool for SimpleLabel

What does this script do?

- Get many images -- ideally with similar light / color conditions
- Create an average image per default using 20 percent of the given images.
  This should reduce the effect of moving things
 - Compare each image with this average image
 - Create boxes around those images
 - If the boxes are larger than a certain size: export them as squared images
 - Those images can be processed by SimpleLabel

TODO:
    - Optimize everything
    - Add a direct upload option
    - Recreate average image from time to time
    - Test the video import feature

"""
# Example from https://pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/
# pip install opencv-python
# pip install imutils


from imutils.video import VideoStream
import argparse
import datetime
import imutils
from imutils import contours
import time
import cv2
import os, sys
from pathlib import Path
import numpy as np
import random
import logging
import csv

REFRESH_REFERENCE_FRAMES = 10

ap = argparse.ArgumentParser()
ap.add_argument("-a", "--min-area", type=float, default=0.0001, help="minimum area size in percent of total pixels, i.e. 0.001 -> 0.1 percent")
ap.add_argument("-o", "--out", type=str, default="out", help="The data output directory")
ap.add_argument("images", nargs="+", help="The series of images")
ap.add_argument("-v", "--video", default=False, action='store_true', help="Input file is a video")
ap.add_argument("-x", "--extra", default=False, action='store_true', help="save intermediate images")
ap.add_argument("-d", "--debug", help="Enable debug messages", action="store_true")
ap.add_argument("-r", "--ref", help="Store the reference frame in the output directory", action="store_true")
ap.add_argument("--imgdb", help="Create an image database with the timestamps", action="store_true")
ap.add_argument("--csvfilename", default="split-info.csv", help="Filename for split information. Default: split-info.csv")

args = vars(ap.parse_args())

if args["debug"]:
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Set logging level to DEBUG")

if args["imgdb"]:
    try:
        import PIL.Image
    except:
        logging.error("Please install PIL")
        sys.exit(1)

    imgdb = []
    for frame_n, image in enumerate(args["images"]):
        img = PIL.Image.open(image)
        modifyDate = img.getexif()[306]
        dt_date = datetime.datetime.strptime(modifyDate, "%Y:%m:%d %H:%M:%S")
        imgdb.append({
            "image" : image,
            "date"  : modifyDate,
            "dt"    : dt_date,
            })

    imgdb.sort(key=lambda x:x["dt"])
    print(imgdb)

    lastframe = None
    for img in imgdb:
        if lastframe is None:
            lastframe = img
            continue
        print((img["dt"] - lastframe["dt"]).total_seconds())
        lastframe = img

        #TODO: Split into sequences, generate average image over sequence, test


    sys.exit(0)


outdir = args["out"]
Path(outdir).mkdir(parents=True, exist_ok=True)

csvfilename = os.path.join(outdir, args["csvfilename"])

additional_images = None
if args["extra"]:
    additional_images = os.path.join(outdir, "extra_images")
    Path(additional_images).mkdir(parents=True, exist_ok=True)

reference_frame = None


# Create union of two boxes, format: x, y, w, h
def union(a,b):
    x = min(a[0], b[0])
    y = min(a[1], b[1])
    w = max(a[0]+a[2], b[0]+b[2]) - x
    h = max(a[1]+a[3], b[1]+b[3]) - y
    return [x, y, w, h]

def _intersect(a,b):
    x = max(a[0], b[0])
    y = max(a[1], b[1])
    w = min(a[0]+a[2], b[0]+b[2]) - x
    h = min(a[1]+a[3], b[1]+b[3]) - y
    if h<0 or w<0:
        return False
    return True

def _group_rectangles(rec):
    """
    Union intersecting rectangles.
    Args:
        rec - list of rectangles in form [x, y, w, h]
    Return:
        list of grouped rectangles
    """
    tested = [False for i in range(len(rec))]
    final = []
    i = 0
    while i < len(rec):
        if not tested[i]:
            j = i+1
            while j < len(rec):
                if not tested[j] and _intersect(rec[i], rec[j]):
                    rec[i] = union(rec[i], rec[j])
                    tested[j] = True
                    j = i
                j += 1
            final.append(rec[i])
        i += 1

    return final

# Extend boxes by for example 40%
def extend_boxes(boxes, percent=40):
    new_boxes = list()
    for box in boxes:
        (x, y, w, h) = box
        center_x = x+(w/2.0)
        center_y = y+(h/2.0)
        w = int(w*(1+(percent/100.0)))
        h = int(h*(1+(percent/100.0)))
        x = int(center_x - (w/2.0))
        y = int(center_y - (h/2.0))
        new_boxes.append((x,y,w,h))
    return new_boxes

# Generate squared boxes as required by ML algorithm
def get_squared_boxes(boxes):
    new_boxes = list()
    for box in boxes:
        (x,y,w,h) = box
        center_x = x+(w/2.0)
        center_y = y+(h/2.0)
        s = max(w, h)
        x = int(center_x - (s/2.0))
        y = int(center_y - (s/2.0))
        new_boxes.append((x, y, s, s))
    return new_boxes

def filter_small_boxes(boxes, min_area):
    output_boxes = []
    for box in boxes:
        if type(box) == np.ndarray:
            if cv2.contourArea(box) < min_area:
                continue

        elif type(box) in (tuple, list) and len(box) == 4:
            if (box[2] * box[3]) < min_area:
                continue

        output_boxes.append(box)

    return output_boxes

def get_avg_image(images, video=False, percentage=20):
    img = None
    if video:
        if len(images) != 1:
            raise ValueError("Only one Video file allowed")
        img = []
        vc = cv2.VideoCapture(images[0])
        n_frames = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))
        get_frames = max(int(n_frames * 0.1), 2)

        for frame_number in random.sample(range(0, n_frames-1), get_frames):
            vc.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = vc.read()
            if ret:
                img.append(frame)

    else:
        number = int(len(images)*percentage/100.0)
        number = max(number, 1) # make sure we have at least one image. TODO: Check / assume a minimum number of images.
        subset = random.sample(images, number)
        img_sub = [cv2.imread(s, 1) for s in subset]
        img = [i for i in img_sub if i is not None] # Make sure all windows can be opened

    img = np.mean(img, axis=0)
    return img.astype("uint8")


reference_frame = cv2.cvtColor(get_avg_image(args["images"]), cv2.COLOR_BGR2GRAY)
reference_frame = cv2.GaussianBlur(reference_frame, (21, 21), 0)

if args["ref"]:
    ref_filename = os.path.join(outdir, "ref_frame.jpg")
    cv2.imwrite(ref_filename, reference_frame)
    logging.debug("Stored reference frame " + str(ref_filename))

with open(csvfilename, 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(("input filename", "y_min", "y_max", "x_min", "x_max", "output filename", "output width", "output height"))

    ## Main func
    for frame_n, image in enumerate(args["images"]):
        # Get plain image name for later storage
        image_name = os.path.basename(image).split(".")
        image_name = (".".join(image_name[:-1]), ".".join(image_name[-1:]))

        img = cv2.imread(image)

        if img is None:
            logging.warning(str(image) + " is not a valid image. Skipping")
            continue

        # Relative min area, smaller areas are ignored
        min_area = int(img.shape[0] * img.shape[1] * args["min_area"])

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        if reference_frame is None:
            reference_frame = gray
            continue

    #    if frame_n%REFRESH_REFERENCE_FRAMES == 0:
    #        #refresh reference frame
    #        reference_frame = gray
    #        continue


        # TODO: get new reference frame every n images?

        frameDelta = cv2.absdiff(reference_frame, gray)

        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        # dilate the thresholded image to fill in holes, then find contours
        # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        cnts = imutils.grab_contours(cnts) # Convenience function for openCV changed behaviour of findContours

        if len(cnts) == 0:
            # No contours found. Next image
            logging.info("No contours found in image " + str(image))
            continue

        (cnts, boundingBoxes) = contours.sort_contours(cnts)

        annotated_img = img.copy()

        annotated_2 = img.copy()
        for bb in boundingBoxes:
            (x, y, w, h) = bb
            cv2.rectangle(annotated_2, (x, y), (x+w, y+h), (0,255,255), 2)

        for bb in get_squared_boxes(boundingBoxes):
            (x, y, w, h) = bb
            cv2.rectangle(annotated_2, (x, y), (x+w, y+h), (255, 0, 0), 2)


        for bb_i, bb in enumerate(get_squared_boxes(filter_small_boxes(_group_rectangles(extend_boxes(get_squared_boxes(boundingBoxes))), min_area))):
            (x, y, w, h) = bb
            cv2.rectangle(annotated_2, (x, y), (x+w, y+h), (0, 0, 255), 2)
            print("#1",x,y,w,h)
            if w < 100:
                logging.info("Ignoring too small box in image " + str(image))
                # Ignore too small images
                continue
            # Shift image if required

            y_min = y
            y_max = y+h
            x_min = x
            x_max = x+w

            print("#2", y_min, y_max, x_min, x_max)

            if y_min < 0:
                y_max = y_max + (-1*y_min)
                y_min = 0

            if x_min < 0:
                x_max = x_max + (-1*x_min)
                x_min = 0

            if x_max >  img.shape[1]:
                x_min = x_min + img.shape[1] - x_max
                x_max = img.shape[1]

            if y_max > img.shape[0]:
                y_min = y_min + img.shape[0] - y_max
                y_max = img.shape[0]
            print("#3",y_min, y_max, x_min, x_max)

            cut_image = img[y_min:y_max, x_min:x_max]
            mid_text = "_cut_squared_"
            if cut_image.shape[0] != cut_image.shape[1]:
                logging.warning("Image not square! " + str(cut_image.shape[0:2]))
                mid_text = "_cut_"
                sys.exit(1)

            filename = os.path.join(outdir, image_name[0]+mid_text+str(bb_i+1)+"."+image_name[1])
            cv2.imwrite(filename, cut_image)
            csvwriter.writerow((".".join(image_name), y_min, y_max, x_min, x_max, filename, cut_image.shape[0], cut_image.shape[1]))
            logging.debug("Created new subimage " + str(filename))



        # loop over the contours
        for c in filter_small_boxes(cnts, min_area):
            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(annotated_img, (x, y), (x + w, y + h), (0, 255, 0), 2)


        if additional_images:
            cv2.imwrite(os.path.join(additional_images, image_name[0]+"_plain_boxes." + image_name[1]), annotated_img)
            cv2.imwrite(os.path.join(additional_images, image_name[0]+"_multiple_boxes." + image_name[1]), annotated_2)
            cv2.imwrite(os.path.join(additional_images, image_name[0]+"_frameDelta." + image_name[1]), frameDelta)
            cv2.imwrite(os.path.join(additional_images, image_name[0]+"_frameThres." + image_name[1]), thresh)









"""

# loop over the frames of the video
while True:
    # grab the current frame and initialize the occupied/unoccupied
    # text
    frame = vs.read()
    frame = frame if args.get("video", None) is None else frame[1]
    text = "Unoccupied"
    # if the frame could not be grabbed, then we have reached the end
    # of the video
    if frame is None:
        break

    # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    # if the first frame is None, initialize it
    if reference_frame is None:# or reference_frame_upd + REFRESH_REFERENCE_SEC < time.time():
        reference_frame = gray
        reference_frame_upd = time.time()
        continue

    # compute the absolute difference between the current frame and
    # first frame
    frameDelta = cv2.absdiff(reference_frame, gray)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < args["min_area"]:
            continue
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = "Occupied"

    # draw the text and timestamp on the frame
    cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    # show the frame and record if the user presses a key
    cv2.imshow("Security Feed", frame)
    cv2.imshow("Thresh", thresh)
    cv2.imshow("Frame Delta", frameDelta)
    key = cv2.waitKey(1) & 0xFF
    # if the `q` key is pressed, break from the lop
    if key == ord("q"):
        break
# cleanup the camera and close any open windows
vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()
"""
