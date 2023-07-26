#!/bin/bash
# Bash Script For Setup And Exec of Training
# Check for correct input

# Assign config path
config_path="$1"
# Check if the folder path is provided
if [ -z "$config_path" ]; then
  echo "Usage: $0 <config_path>"
  exit 1
else
  echo "Using config ${config_path}"
fi

echo "***************************GPU INFO********************************"
nvidia-smi
echo "************************Beginning Training************************"
# Find the number or partitions in the dataset
# Loop through the subdirectories in the provided path
num_partitions=0  # Initialize num_partitions to zero
i=1  # Start with i=1
while true; do
    subdir="/workspace/dataset/yolo_mots/par${i}"
    # Check if the subdirectory exists
    if [ -d "${subdir}" ]; then
        num_partitions=$((num_partitions + 1))  # Increment num_partitions
        i=$((i + 1))  # Move to the next number
    else
        # If the subdirectory doesn't exist, break out of the loop
        break
    fi
done

# Output the result
echo "Training on ${num_partitions} partitions"

# Read in config
# Argument Setup: https://stackoverflow.com/questions/5014632/how-can-i-parse-a-yaml-file-from-a-linux-shell-script
parse_yaml() {
   local prefix=$2
   local s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @|tr @ '\034')
   sed -ne "s|^\($s\):|\1|" \
        -e "s|^\($s\)\($w\)$s:$s[\"']\(.*\)[\"']$s\$|\1$fs\2$fs\3|p" \
        -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p"  $1 |
   awk -F$fs '{
      indent = length($1)/2;
      vname[indent] = $2;
      for (i in vname) {if (i > indent) {delete vname[i]}}
      if (length($3) > 0) {
         vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
         printf("%s%s%s=\"%s\"\n", "'$prefix'",vn, $2, $3);
      }
   }'
}

eval $(parse_yaml ${config_path})

# Establish yaml modification
update_yaml_field() {
  local yaml_file="$1"
  local field_name="$2"
  local new_contents="$3"

  # Check if the YAML file exists
  if [ ! -f "$yaml_file" ]; then
    echo "YAML file '$yaml_file' not found."
    return 1
  fi

  # Update the field in the YAML file using sed
  sed -i "s|\($field_name: \).*|\1$new_contents|" "$yaml_file"

  echo "Field '$field_name' in '$yaml_file' updated to '$new_contents'."
}

# Create a working copy of the config file
cp $config_path config_temp.yaml

# Establish function for checking if results file has been written
check_file() {
if [ -s "$1" ]; then
    return 0
else
    return 1
fi
}

initial=1
chkpt_path=""
max_wait_time=30
check_interval=1
echo "Running training for ${global_epochs} GLOBAL EPOCHS"
# Loop from 1 to global_epochs
z=1
while [ "$z" -le "$global_epochs" ]; do
    # Loop through partitions
    i=1
    while [ "$i" -le "$num_partitions" ]; do
        echo "************************Training Partition ${i}************************"
        update_yaml_field "config_temp.yaml" "data_dir" "${data_dir}/par${i}"
        update_yaml_field "config_temp.yaml" "experiment_train" "${experiment_train}_par${i}e${z}"

        # Start waiting for checkpoint file to be written
        elapsed_time=0
        echo "Waiting for checkpoint file to be written in ${chkpt_path}"
        while [ $elapsed_time -lt $max_wait_time ]; do
            # 1st iteration has no checkpoint
            if [ "$initial" -eq 1 ]; then
                initial=0
                sh train.sh config_temp.yaml
                break;
            fi
            # If checkpoint found, proceed with training
            if check_file "$chkpt_path"; then
                echo "Checkpoint found. Proceeding with training..."
                sh train.sh config_temp.yaml
                break
            fi
            # Wait for an interval and increment elapsed time
            echo -n "."
            sleep $check_interval
            elapsed_time=$((elapsed_time + check_interval))
        done
        pwd
        ls /
        find / -type d -name "test_run_par1"

        # Timeout Message
        if [ $elapsed_time -ge $max_wait_time ]; then
            echo "Timed out. File not found within the specified time."
        fi
        
        # Update checkpoint path in config
        chkpt_path="/workspace/dataset/yolo_mots/par${i}/${project_train}/${experiment_train}_par${i}e${z}/weights/last.pt"
        update_yaml_field "config_temp.yaml" "model" "${chkpt_path}"
        i=$((i + 1))
    done
    z=$((z + 1))
done

# Copy over results when done
mv /workspace/${project_train}/ /workspace/dataset/
