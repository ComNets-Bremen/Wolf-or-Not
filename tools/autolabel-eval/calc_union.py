#!/usr/bin/env python3

"""
Jens Dede, jd@comnets-uni-bremen.de

Ref: https://towardsdatascience.com/confusion-matrix-and-object-detection-f0cbcb634157
"""
import argparse

import os, sys
import glob

parser = argparse.ArgumentParser(description="Evaluate two sets of label date and calculate the IOU")
parser.add_argument("ground_truth", type=str, help="The directory with the ground truth labels.")
parser.add_argument("testdata", type=str, help="The directory with the test truth labels.")
parser.add_argument('--ext', type=str, default="txt", help="The file extension for the labels")
parser.add_argument('--threshold', type=float, default=0.5, help="The threshold for the IOU calculation")
parser.add_argument('--verbose', '-v', action='store_true', help="Be verbose")
args = parser.parse_args()


def bbox_iou(box1, box2):
    """
    Returns the IoU of two bounding boxes
    """
    # Transform from center and width to exact coordinates
    b1_x1, b1_x2 = box1[0] - box1[2] / 2, box1[0] + box1[2] / 2
    b1_y1, b1_y2 = box1[1] - box1[3] / 2, box1[1] + box1[3] / 2
    b2_x1, b2_x2 = box2[0] - box2[2] / 2, box2[0] + box2[2] / 2
    b2_y1, b2_y2 = box2[1] - box2[3] / 2, box2[1] + box2[3] / 2

    # get the coordinates of the intersection rectangle
    inter_rect_x1 = max(b1_x1, b2_x1)
    inter_rect_y1 = max(b1_y1, b2_y1)
    inter_rect_x2 = min(b1_x2, b2_x2)
    inter_rect_y2 = min(b1_y2, b2_y2)

    # Intersection area
    #inter_area = torch.clamp(inter_rect_x2 - inter_rect_x1, min=0) * torch.clamp(
    #    inter_rect_y2 - inter_rect_y1, min=0
    #)
    inter_area = max(0, inter_rect_x2 - inter_rect_x1) * max(0, inter_rect_y2 - inter_rect_y1)
    # Union Area
    b1_area = (b1_x2 - b1_x1 ) * (b1_y2 - b1_y1 )
    b2_area = (b2_x2 - b2_x1 ) * (b2_y2 - b2_y1 )

    iou = inter_area / (b1_area + b2_area - inter_area + 1e-16)

    return iou

def check_iou(gt, det):
    # Format: Class, xCenter, yCenter, w, h
    list_gt  = []
    list_det = []

    for g in gt:
        if len(g) == 0:
            continue
        list_gt.append({
                "raw" : g,
                "class" : int(g[0]),
                "detected" : False,
                "box" : [float(x) for x in g.split()[1:]],
            })

    for d in det:
        if len(d) == 0:
            continue
        list_det.append({
                "raw" : d,
                "class" : int(d[0]),
                "detected" : False,
                "box" : [float(x) for x in d.split()[1:]],
            })


    tp = 0
    tn = 0 #not possible in image recognition
    fp = 0
    fn = 0

    for i in range(len(list_gt)):
        for j in range(len(list_det)):
            box_correct  = bbox_iou(list_gt[i]["box"], list_det[j]["box"]) > args.threshold
            same_class   = list_gt[i]["class"] == list_det[j]["class"]
            gt_detected  = list_gt[i]["detected"]
            det_detected = list_det[j]["detected"]

            if box_correct and same_class and not gt_detected and not det_detected:
                tp=tp+1
                list_gt[i]["detected"] = True
                list_det[j]["detected"] = True

            elif box_correct and not same_class and not gt_detected and not det_detected:
                fp=fp+1
                list_gt[i]["detected"] = True
                list_det[j]["detected"] = True

    for l in list_gt:
        # boxes in ground truth not detected: False Negative
        if not l["detected"]:
            fn = fn + 1
    for l in list_det:
        if not l["detected"]:
            fp = fp + 1

    return {"fp" : fp, "tp" : tp, "fn" : fn, "tn" : tn}



t_detections = glob.glob(os.path.join(args.testdata, "*."+args.ext))
t_ground_truth = glob.glob(os.path.join(args.ground_truth, "*."+args.ext))

s_detections = set([os.path.basename(f) for f in t_detections])
s_ground_truth = set([os.path.basename(f) for f in t_ground_truth])
s_all_files = s_detections.union(s_ground_truth)

sumdata =  {"fp" : 0, "tp" : 0, "fn" : 0, "tn" : 0}


for f in s_all_files:
    detection = []
    ground_truth = []
    try:
        fh_detection = open(os.path.join(args.testdata, f), "r")
        detection = fh_detection.read().split("\n")
    except FileNotFoundError:
        detection = []
    finally:
        try:
            fh_detection.close()
        except NameError:
            print("No detections found. Are you using the correct datasets?")
            sys.exit(1)

    try:
        fh_ground_truth = open(os.path.join(args.ground_truth, f), "r")
        ground_truth = fh_ground_truth.read().split("\n")
    except FileNotFoundError:
        ground_truth = []
    finally:
        fh_ground_truth.close()

    r = check_iou(ground_truth, detection)

    for d in r:
        sumdata[d] = sumdata[d] + r[d]

    if args.verbose:
        print(f, r)


precision = sumdata["tp"] / (sumdata["tp"] + sumdata["fp"])
recall    = sumdata["tp"] / (sumdata["tp"] + sumdata["fn"])
f1        = 2*((precision * recall) / (precision + recall))

print(sumdata)
print("Precision", precision)
print("Recall", recall)
print("F1 score", f1)
