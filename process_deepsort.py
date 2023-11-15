import cv2 as cv
import json
import os
import os.path as path
from os.path import join, isfile
import argparse
from utils import class_dict
from utils import clean_list, update_prog
from im_publish.publish import ImageStreamer


# Parameter Defaults
label_path_d = "C:\\Users\\dylan\\Documents\\Data\\BDD100k_MOT202\\labels\\"
vid_path_d = "C:\\Users\\dylan\\Documents\\Data\\BDD100k_MOT202\\bdd100k\\"
dest_path_d = "C:\\Users\\dylan\\Documents\\Data\\YOLO_MOTS"
preview_d = False
object_limit_d = 3000
inst_limit_d = 10000
overwrite_dataset_d = True
port_d = 5000

'''Function to add arguments'''
def init_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', type=str, default=vid_path_d, help='Path to bdd100k dataset')
    parser.add_argument('--dst', type=str, default=dest_path_d, help='Path to save processed data')
    parser.add_argument('--prev', type=bool, default=False, help='Preview conversion')
    parser.add_argument('--owrt', type=bool, default=False, help='Overwrite Dataset')
    parser.add_argument('--lim', type=int, default=object_limit_d, help='Limit of images processed')
    parser.add_argument('--ilim', type=int, default=inst_limit_d, help='Limit of instances processed')
    parser.add_argument('--port', type=int, default=port_d, help="Port to publish previews")
    parser.add_argument('--diag', type=bool, default=False, help="Diagostic information on the dataset")
    return parser

def main_func(args):
    # Assign arguments
    source_path = args.src
    dest_path = args.dst
    overwrite_dataset = args.owrt
    object_limit = args.lim
    inst_limit = args.ilim
    preview = args.prev
    port = args.port
    diagnose = args.diag
    partition_number = 1

    # Create Initial Partition
    os.makedirs(dest_path, exist_ok=True)
    os.makedirs(os.path.join(dest_path, "train"), exist_ok=True)
    os.makedirs(os.path.join(dest_path, "val"), exist_ok=True)

    # Calculate number of training and validation samples
    label_train_path = os.path.join(source_path, "labels", "box_track_20", "train")
    num_train_samples = len(clean_list(os.listdir(label_train_path), '.json'))
    label_val_path = os.path.join(source_path, "labels", "box_track_20", "val")
    num_val_samples = len(clean_list(os.listdir(label_val_path), '.json'))
    print("Processing: "+str(num_train_samples)+" training samples + "+str(num_val_samples)+" validation samples")
    val_target = int(object_limit/3)

    if diagnose:
        for split in ["train", "val"]:
            # Find the image and label paths for the split
            split_path = join(dest_path, split)
            print_dataset_stats(split_path)

    # If previewing, setup streamwriter
    streamer = ImageStreamer(port=port, debug=False)

    object_count = 0
    # Main Loop for Train/Val Split
    for split in ["train", "val"]:
        # Find the image and label paths for the split
        label_path = os.path.join(source_path, "labels", "box_track_20", split)
        vid_path = os.path.join(source_path, "images", "track", split)
        split_path = os.path.join(dest_path, split)

        # Get Label IDs for split
        label_ids = clean_list(os.listdir(label_path), '.json')

        # Get existing image labels from the labels folder
        print("Checking existing data...")
        existing_dirs = [x[0] for x in os.walk(split_path)]
        # Prune unfinished and small data
        for i, dir in enumerate(existing_dirs):
            if os.path.exists(join(split_path, dir)):
                files = [f for f in os.listdir(join(split_path, dir)) if isfile(join(split_path, dir, f))]
                if len(files) < 2:
                    del existing_dirs[i]

        skipping = True

        # Split Conditionals
        if split == "train":
            print("Processing Training Data...")
        elif split == "val":
            print("Processing Validation Data...")

        # Main Loop for writing video frames to dataset
        objects_processed = 0
        instances_processed = 0
        for id in label_ids:
            # Update Display of Percentage
            if split=="train":
                percent = (objects_processed/object_limit)*100
            elif split=="val":
                percent = (objects_processed/val_target)*100
            update_prog(partition_number, percent)


            # Pull Json for the given video
            with open(path.join(label_path, id+".json")) as file:
                label_data = json.load(file)

            # Define Filepath For Frames
            im_path = path.join(vid_path, id)

            # For Each Frame
            for frame_data in label_data:
                if frame_data["name"][:-4] not in existing_dirs:
                    skipping = False
                    # Get Image
                    im = cv.imread(path.join(im_path, frame_data["name"]))

                    # Get Bounding Box Data
                    for detection in frame_data["labels"]:
                        id = detection["id"]
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
                        
                        # Extract ROI
                        roi = im[y1:y2,x1:x2]

                        # Create Folder for object if none exists
                        save_path = os.path.join(split_path,id)
                        if not os.path.exists(save_path):
                            os.mkdir(save_path)
                            objects_processed = objects_processed + 1
                            im_num = 0
                        else:
                            im_num = len(os.listdir(save_path))

                        # Save roi to id folder
                        if roi:
                            cv.imwrite(os.path.join(save_path, f"{im_num}.jpg"), roi)

                            if preview:
                                desc = f"Object {objects_processed})({id}), Instance {instances_processed}"
                                streamer.publish_frame(im=roi, desc=desc)
                        
                            # Increment
                            instances_processed = instances_processed + 1
                        
                # Increment Frames Considered
                if (objects_processed >= object_limit and split=="train") or (objects_processed >= val_target and split=="val") or instances_processed > inst_limit:
                    break

            # Break out of videos if dataset limit is reached
            if (objects_processed >= object_limit and split=="train") or (objects_processed >= val_target and split=="val") or instances_processed > inst_limit:
                    break
    
    if diagnose:
        for split in ["train", "val"]:
            # Find the image and label paths for the split
            split_path = join(dest_path, split)
            print_dataset_stats(split_path)
            

    print("Done!")

def print_dataset_stats(path):
    num_images = []
    print("Scanning dirs...")
    obj_dirs = [x for x in os.listdir(path) if os.path.isdir(join(path, x))]
    total_objects = len(obj_dirs)
    total_inst = 0
    for dir in obj_dirs:
        print(f"\rCounting Files...{total_inst}")
        total_inst += len([x for x in os.listdir(join(path,dir)) if os.path.isfile(join(path,dir,x))])
    average_inst = total_inst/total_objects if (total_objects != 0) else 0
    print(f"\r{path} Dataset: {total_objects} objects, {total_inst} instances, {average_inst} average inst/obj")


if __name__ == '__main__':
    args =  init_parser().parse_args()
    print(args)
    main_func(args)
