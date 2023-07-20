import yaml
import os
import shutil
import json
import sys
from math import floor, ceil

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

def create_parition(filepath, overwrite_dataset=True):
    # Create File Structure
    train_path = os.path.join(filepath, "train")
    val_path = os.path.join(filepath, "val")
    test_path = os.path.join(filepath, "test")
    train_im_path = os.path.join(filepath, "train", "images")
    train_label_path = os.path.join(filepath, "train", "labels")
    val_im_path = os.path.join(filepath, "val", "images")
    val_label_path = os.path.join(filepath, "val", "labels")
    mkdir_safe(filepath, overwrite_contents=overwrite_dataset)
    mkdir_safe(train_path, overwrite_contents=overwrite_dataset)
    mkdir_safe(train_label_path, overwrite_contents=overwrite_dataset)
    mkdir_safe(train_im_path, overwrite_contents=overwrite_dataset)
    mkdir_safe(val_path, overwrite_contents=overwrite_dataset)
    mkdir_safe(val_label_path, overwrite_contents=overwrite_dataset)
    mkdir_safe(val_im_path, overwrite_contents=overwrite_dataset)
    mkdir_safe(test_path, overwrite_contents=overwrite_dataset)

    # Create .yaml for ultralytics API
    write_yaml_file(filename="data.yaml",
                    root_path=filepath,
                    train_path=train_path,
                    val_path=val_path,
                    test_path=test_path,
                    class_dict=class_dict)
    write_yaml_file(filename="data_bash.yaml",
                    root_path=filepath,
                    train_path=win2bash(train_path),
                    val_path=win2bash(train_path),
                    test_path=win2bash(test_path),
                    class_dict=class_dict)

def write_partition_info(filepath, train_samples, validation_samples):
    partition_info = {
        "train_samples": train_samples,
        "validation_samples": validation_samples
    }
    with open(os.path.join(filepath,"partition_info.json"), "w") as file:
        json.dump(partition_info, file)

def read_validation_target(filepath):
    with open(os.path.join(filepath,"partition_info.json"), "r") as file:
        data = json.load(file)
        validation_samples = data["validation_samples"]
        train_samples = data["train_samples"]
    return validation_samples

def update_prog(partition_number, percent):
    sys.stdout.write('\r')
    sys.stdout.write(
        "Partition %s: [%-20s] %d%%" % (str(partition_number), '=' * floor(percent * .2), percent))
    sys.stdout.flush()
