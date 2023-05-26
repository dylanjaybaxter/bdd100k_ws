'''
This Script is intended to test YOLOv8 formatting
'''
# Imports
import pandas as pd
import argparse
import re
import cv2 as cv
import os
from os import path
import shutil
from math import floor


# Defaults for use as a script
dim_dir = "C:\\Users\\dylan\\Documents\\Data\\YOLO_MOTS\\train\\images"
dlabel_dir = "C:\\Users\\dylan\\Documents\\Data\\YOLO_MOTS\\train\\labels"

'''Function to add arguments'''
def init_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ims', type=str, default=dim_dir, help='Path to images')
    parser.add_argument('--lbls', type=str, default=dlabel_dir, help='Path to labels')
    return parser

'''Main function'''
def main_func(args):
    im_files = os.listdir(args.ims)
    label_files = os.listdir(args.lbls)

    for im_file in im_files:
        im_path = os.path.join(args.ims, im_file)
        base_name = im_file[:-4]
        label_path = os.path.join(args.lbls, base_name+".txt")
        im = cv.imread(im_path)
        im_h = im.shape[0]
        im_w = im.shape[1]
        labels = read_floats(label_path)
        for label in labels:
            cx = floor(label[1] * im_w)
            cy = floor(label[2] * im_h)
            w = floor(label[3] * im_w)
            h = floor(label[4] * im_h)
            x1 = cx - floor(w/2)
            x2 = cx + floor(w/2)
            y1 = cy - floor(h/2)
            y2 = cy + floor(h/2)

            cv.rectangle(im, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv.line(im, (cx+10, cy), (cx-10, cy), (255, 0, 0), 2)
            cv.line(im, (cx, cy+10), (cx, cy-10), (255, 0, 0), 2)
        im = cv.resize(im, (1280, 720))
        cv.imshow("Frame", im)
        cv.waitKey(1)

    print("Done!")


def read_floats(filename):
    """
    Reads in multiple space-delimited floats from a file, creating a new list of values for each new line in the file.

    Args:
    filename (str): the name of the file to read from

    Returns:
    A list of lists, where each inner list contains the floats from a single line in the file
    """
    with open(filename, 'r') as file:
        lines = file.readlines()
        floats_list = []
        for line in lines:
            floats = list(map(float, line.split()))
            floats_list.append(floats)
        return floats_list





if __name__ == '__main__':
    args =  init_parser().parse_args()
    print(args)
    main_func(args)
