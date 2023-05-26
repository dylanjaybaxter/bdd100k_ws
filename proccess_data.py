import cv2 as cv
import json
import os
import os.path as path
import shutil
import yaml

label_path = "C:\\Users\\dylan\\Documents\\Data\\BDD100k_MOT202\\train\\labels\\"
vid_path = "C:\\Users\\dylan\\Documents\\Data\\BDD100k_MOT202\\train\\images\\"

dest_path = "C:\\Users\\dylan\\Documents\\Data\\YOLO_MOTS"
preview = False
dataset_limit = 50000
overwrite_dataset = True

class_dict = {
    "pedestrian": 0,
    "other person": 0,
    "rider": 1,
    "bicycle": 1,
    "car": 2,
    "motorcycle": 3,
    "bus": 5,
    "train": 6,
    "truck": 7,
    "other vehicle": 2,
    "trailer": 6
}

coco_classes = [
  "person",
  "bicycle",
  "car",
  "motorcycle",
  "airplane",
  "bus",
  "train",
  "truck",
  "boat",
  "traffic light",
  "fire hydrant",
  "stop sign",
  "parking meter",
]

def clean_list(label_ids, ext):
    # create a new list to store the cleaned up file names
    cleaned_list = []

    # iterate over each file in the original list
    for file_name in label_ids:
        # check if the file name contains the '.json' extension
        if ext in file_name:
            # remove the '.json' extension from the file name
            file_name = file_name.replace(ext, '')
            # add the cleaned up file name to the new list
            cleaned_list.append(file_name)

    # replace the original list with the cleaned up list
    return cleaned_list

def mkdir_safe(dir_path, overwrite_contents):
    # Check if the directory path
    if os.path.exists(dir_path):
        # Check if there are files in the directory
        if len(os.listdir(dir_path)) == 0:
            return False
        elif overwrite_contents:
            shutil.rmtree(dir_path, ignore_errors=True)
            os.mkdir(dir_path)
            return True
        else:
            return False
    else:
        os.mkdir(dir_path)
        return True


def write_yaml_file(filename, root_path, train_path, val_path, test_path, class_dict):
  """Writes a YAML file in the following format:

  # Train/val/test sets as 1) dir: path/to/imgs, 2) file: path/to/imgs.txt, or 3) list: [path/to/imgs1, path/to/imgs2, ..]
  path: ../datasets/coco128  # dataset root dir
  train: images/train2017  # train images (relative to 'path') 128 images
  val: images/train2017  # val images (relative to 'path') 128 images
  test:  # test images (optional)

  # Classes (80 COCO classes)
  names:
    0: person
    1: bicycle
    2: car
    ...
    77: teddy bear
    78: hair drier
    79: toothbrush

  Args:
    names: A dictionary of class names to IDs.
    paths: A set of strings for the paths.

  """

  with open(os.path.join(root_path, filename), "w") as f:
    yaml.dump({
      "names": coco_classes,
      "nc": len(coco_classes),
      "path": root_path,
      "train": train_path,
      "val": val_path,
      "test": test_path
    }, f, default_flow_style=False)

def win2bash(powershell_filepath):
  """Converts a PowerShell filepath to a Windows Bash filepath.
  Args:
    powershell_filepath: The PowerShell filepath to convert.
  Returns:
    The Windows Bash filepath.
  """
  # Replace `\\` with `/`.
  powershell_filepath = powershell_filepath.replace("\\", "/")
  # Convert `C:` to `/mnt/c`.
  if powershell_filepath.startswith("C:"):
    powershell_filepath = "/mnt/c" + powershell_filepath[2:]

  return powershell_filepath



# Create File Sttructure
train_path = os.path.join(dest_path, "train")
val_path = os.path.join(dest_path, "val")
test_path = os.path.join(dest_path, "test")
train_vid_path = os.path.join(dest_path, "vids")
train_im_path = os.path.join(dest_path, "train", "images")
train_label_path = os.path.join(dest_path, "train", "labels")
mkdir_safe(dest_path, overwrite_contents=overwrite_dataset)
mkdir_safe(train_path, overwrite_contents=overwrite_dataset)
mkdir_safe(train_vid_path, overwrite_contents=overwrite_dataset)
mkdir_safe(train_label_path, overwrite_contents=overwrite_dataset)
mkdir_safe(train_im_path, overwrite_contents=overwrite_dataset)
mkdir_safe(val_path, overwrite_contents=overwrite_dataset)
mkdir_safe(test_path, overwrite_contents=overwrite_dataset)

# Create .yaml for ultralytics API
write_yaml_file(filename="data.yaml",
                root_path=dest_path,
                train_path=train_path,
                val_path=val_path,
                test_path=test_path,
                class_dict=class_dict)
write_yaml_file(filename="data_bash.yaml",
                root_path=dest_path,
                train_path=win2bash(train_path),
                val_path=win2bash(train_path),
                test_path=win2bash(test_path),
                class_dict=class_dict)


# Get Label IDs
label_ids = clean_list(os.listdir(label_path), '.json')

# Get existing image labels from the labels folder
existing_labels = clean_list(os.listdir(train_label_path), ".txt")
skipping = True
proccessed = 0
for id in label_ids:
    # Pull Json for the given video
    with open(path.join(label_path, id+".json")) as file:
        label_data = json.load(file)

    # Define Filepath For Frames
    im_path = path.join(vid_path, id)

    # Create Vid Folder
    mkdir_safe(path.join(train_vid_path, id), overwrite_contents=False)

    # For Each Frame
    for frame_data in label_data:
        if frame_data["name"][:-4] not in existing_labels:
            if skipping is True:
                print("Beginning to process real frames...")
            skipping = False
            # Get Image
            im = cv.imread(path.join(im_path, frame_data["name"]))
            im_w = im.shape[1]
            im_h = im.shape[0]
            im_overlay = im

            # Initialize Label File
            f = open(path.join(train_label_path, frame_data["name"][:-4]+".txt"), 'w')
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
                with open(path.join(train_label_path, frame_data["name"][:-4]+".txt"), 'a') as file:
                    # file.write(f"{str(SHARK_LABEL)} {str(x1 / im_w)} {str(y1 / im_h)} {str(w / im_w)} {str(h / im_h)}")
                    file.write(f"{str(cat_id)} {str(cx / im_w)} {str(cy / im_h)} {str(w / im_w)} {str(h / im_h)}\n")

            # Copy matching image to images folder
            shutil.copy(path.join(im_path, frame_data["name"]), path.join(train_vid_path, id, frame_data["name"]))
            shutil.copy(path.join(im_path, frame_data["name"]), path.join(train_im_path, frame_data["name"]))

            if proccessed >= dataset_limit:
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
        proccessed = proccessed + 1
        if proccessed >= dataset_limit:
            break
    if proccessed >= dataset_limit:
        break



print("Done!")