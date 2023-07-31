import cv2 as cv
import json
import os
import os.path as path
import shutil
import yaml
import argparse
from math import floor
from math import ceil
import sys
from utils import class_dict, coco_classes
from utils import mkdir_safe, write_yaml_file, win2bash, clean_list, update_prog
from utils import write_partition_info, read_validation_target, create_parition


# Parameter Defaults
label_path_d = "C:\\Users\\dylan\\Documents\\Data\\BDD100k_MOT202\\labels\\"
vid_path_d = "C:\\Users\\dylan\\Documents\\Data\\BDD100k_MOT202\\bdd100k\\"
dest_path_d = "C:\\Users\\dylan\\Documents\\Data\\YOLO_MOTS"
preview_d = False
dataset_limit_d = 3000
partition_limit_d = 1000
overwrite_dataset_d = True

'''Function to add arguments'''
def init_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', type=str, default=vid_path_d, help='Path to bdd100k dataset')
    parser.add_argument('--dst', type=str, default=dest_path_d, help='Path to save processed data')
    parser.add_argument('--prev', type=bool, default=False, help='Preview conversion')
    parser.add_argument('--owrt', type=bool, default=False, help='Overwrite Dataset')
    parser.add_argument('--limit', type=int, default=dataset_limit_d, help='Limit of images processed')
    parser.add_argument('--plimit', type=int, default=partition_limit_d, help='Limit of images per partition')
    return parser

def main_func(args):
    # Assign arguments
    source_path = args.src
    dest_path = args.dst
    overwrite_dataset = args.owrt
    dataset_limit = args.limit
    preview = args.prev
    partition_limit = args.plimit
    partition_number = 1

    # Create Initial Partition
    print("Writing Initial Partition: "+ os.path.join(dest_path, "par"+str(partition_number))+ "...")
    print("Overwriting: "+ str(overwrite_dataset))
    create_parition(os.path.join(dest_path, "par"+str(partition_number)), overwrite_dataset=overwrite_dataset)

    # Calculate number of training and validation samples
    label_train_path = os.path.join(source_path, "labels", "box_track_20", "train")
    num_train_samples = len(clean_list(os.listdir(label_train_path), '.json'))
    label_val_path = os.path.join(source_path, "labels", "box_track_20", "val")
    num_val_samples = len(clean_list(os.listdir(label_val_path), '.json'))
    partitions_needed = ceil(num_train_samples/partition_limit)
    # Update Dataset Limit to the number of samples
    dataset_limit = min(dataset_limit, num_train_samples*60)
    partition_limit = min(partition_limit, num_train_samples*60)
    print("Processing: " + str(num_train_samples) + " training samples + " + str(num_val_samples) + " validation samples")
    print(f"Partitions Estimate: {partitions_needed} (size: {partition_limit})")
    print(f"Partition Limit: {ceil(dataset_limit/partition_limit)} with data limit {dataset_limit}")



    processed = 0
    partition_processed = 0
    # Main Loop for Train/Val Split
    for split in ["train", "val"]:
        # Find the image and label paths for the split
        partition_number = 1
        label_path = os.path.join(source_path, "labels", "box_track_20", split)
        vid_path = os.path.join(source_path, "images", "track", split)
        par_path = os.path.join(dest_path, "par"+str(partition_number))
        label_path_dest = os.path.join(par_path,  split, "labels")
        im_path_dest = os.path.join(par_path, split, "images")

        # Get Label IDs for split
        label_ids = clean_list(os.listdir(label_path), '.json')

        # Get existing image labels from the labels folder
        existing_labels = clean_list(os.listdir(label_path_dest), ".txt")
        skipping = True

        # Split Conditionals
        if split == "train":
            print("Processing Training Data...")
            val_target = 0
        elif split == "val":
            print("Processing Validation Data...")
            # Get initial validation target
            val_target = read_validation_target(par_path)

        # Main Loop for writing video frames to dataset
        partition_processed = 0
        for id in label_ids:
            # Update Display of Percentage
            if split=="train":
                percent = (partition_processed/min(partition_limit, dataset_limit))*100
            elif split=="val":
                percent = (partition_processed/val_target)*100
            update_prog(partition_number, percent)


            # Pull Json for the given video
            with open(path.join(label_path, id+".json")) as file:
                label_data = json.load(file)

            # Define Filepath For Frames
            im_path = path.join(vid_path, id)

            # Determine if new video exceeds partition limit
            if len(label_data)+partition_processed > partition_limit:
                # If no files have been written, move on to next video
                if partition_processed == 0:
                    print("Video is too large for current partition size. Skipping...")
                    continue
                # If we've just run out of room in the partition, move onto the next one
                else:
                    #  If training write partition information to json
                    if split == "train":
                        val_target = floor((partition_processed / num_train_samples) * num_val_samples)
                        write_partition_info(par_path, partition_processed, val_target)
                        update_prog(partition_number, 100)
                        print("\nTraining images for partition " + str(partition_number) + " complete: " + \
                              str(partition_processed) + " training images, " + str(val_target) + " validation target")
                    else:
                        print("\nValidation images for partition " + str(partition_number) + " complete: " + \
                              + str(partition_processed) + " validation images")
                    # Move to next partition number
                    partition_number = partition_number + 1
                    # Reset Processed Counter
                    partition_processed = 0
                    # Update partition path and create a new partition
                    par_path = os.path.join(dest_path, "par" + str(partition_number))
                    label_path_dest = os.path.join(par_path, split, "labels")
                    im_path_dest = os.path.join(par_path, split, "images")
                    create_parition(par_path, overwrite_dataset=True)

            # For Each Frame
            for frame_data in label_data:
                if frame_data["name"][:-4] not in existing_labels:
                    skipping = False
                    # Get Image
                    im = cv.imread(path.join(im_path, frame_data["name"]))
                    im_w = im.shape[1]
                    im_h = im.shape[0]
                    im_overlay = im

                    # Initialize Label File
                    f = open(path.join(label_path_dest, frame_data["name"][:-4]+".txt"), 'w')
                    f.close()

                    # Get Bounding Box Data
                    for detection in frame_data["labels"]:
                        cat = detection["category"]
                        if cat not in class_dict:
                            print("No ID for: "+ cat+ "in "+frame_data["name"]+", assigning to \'other vehicle\'")
                            cat_id = class_dict["other vehicle"]
                        else:
                            cat_id = class_dict[cat]
                        x1 = int(detection["box2d"]["x1"])
                        x2 = int(detection["box2d"]["x2"])
                        y1 = int(detection["box2d"]["y1"])
                        y2 = int(detection["box2d"]["y2"])
                        w = abs(x2-x1)
                        h = abs(y2-y1)
                        cx = x1+abs(x1-x2)/2
                        cy = y1+abs(y1-y2)/2

                        norms = [x1 / im_w, y1 / im_h, x2 / im_w, y2 / im_h]
                        if max(norms) > 1:
                            print("FORMATTING: OUT OF BOUNDS ERROR")

                        # Normalize values by im dimensions and save to file, YOLO format
                        with open(path.join(label_path_dest, frame_data["name"][:-4]+".txt"), 'a') as file:
                            file.write(f"{str(cat_id)} {str(cx / im_w)} {str(cy / im_h)} {str(w / im_w)} {str(h / im_h)}\n")

                    # Copy matching image to images folder
                    shutil.copy(path.join(im_path, frame_data["name"]), path.join(im_path_dest, frame_data["name"]))

                    if processed >= dataset_limit:
                        break

                    if preview:
                        cv.rectangle(im_overlay, (x1, y1), (x2, y2), (0, 255, 0), 2)

                        text = detection["category"] + ": " + detection["id"]

                        # Define the font and font scale
                        font = cv.FONT_HERSHEY_SIMPLEX
                        font_scale = 0.5

                        # Get the size of the text
                        (text_width, text_height), _ = cv.getTextSize(text, font, font_scale, thickness=1)

                        # Calculate the coordinates for the text
                        text_x = x1 + (abs(x2 - x1) - text_width) // 2
                        text_y = y1 + (abs(y2 - y1) + text_height) // 2

                        # Write the text on the image
                        cv.putText(im_overlay, text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness=2)

                        # Show Image
                        cv.imshow("Dataset Preview", im_overlay)
                        cv.waitKey(1)
                else:
                    if skipping is False:
                        print("Skipping Frames where labels already exist...")
                    skipping = True

                # Increment Frames Considered
                processed = processed + 1
                partition_processed = partition_processed + 1
                if (processed >= dataset_limit and split=="train") or (partition_processed >= val_target and split=="val"):
                    break

            # Break out of videos if dataset limit is reached
            if (processed >= dataset_limit and split=="train"):
                val_target = floor((partition_processed / num_train_samples) * num_val_samples)
                write_partition_info(par_path, partition_processed, val_target)
                update_prog(partition_number, 100)
                print("\nTraining images for partition " + str(partition_number) + " complete: " +
                      str(partition_processed) + " training images, " + str(val_target) + " validation target")
                break
            elif (partition_processed >= val_target and split=="val"):
                update_prog(partition_number, 100)
                print("\nValidation images for partition " + str(partition_number) + " complete: "
                      + str(partition_processed) + " validation images")
                # Move to next partition number
                partition_number = partition_number + 1
                # Reset Processed Counter
                partition_processed = 0
                # Update partition path and create a new partition
                par_path = os.path.join(dest_path, "par" + str(partition_number))
                label_path_dest = os.path.join(par_path, split, "labels")
                im_path_dest = os.path.join(par_path, split, "images")
                if os.path.exists(par_path):
                    val_target = read_validation_target(par_path)
                else:
                    break


        processed = 0

    print("Done!")

if __name__ == '__main__':
    args =  init_parser().parse_args()
    print(args)
    main_func(args)
