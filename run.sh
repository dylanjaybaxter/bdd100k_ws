# Bash Script For Setup And Exec of Training
# Check for correct input

# Assign config path
config_path="$1"
# Check if the folder path is provided
if [ -z "$config_path" ]; then
  echo "Usage: $0 <config_path>"
  exit 1
fi

#!/bin/bash
echo "***************************GPU INFO********************************"
nvidia-smi
echo "************************Beginning Training************************"
# Find the number or partitions in the dataset
# Loop through the subdirectories in the provided path
for subdir in "$1"/par*; do
# Check if the subdirectory matches the naming convention [par1, par2, par3, ...]
if [ -d "${subdir}" ] && [[ "${subdir}" =~ ^"$1"/par[0-9]+$ ]]; then
    num_partitions=$((num_partitions + 1))
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


initial=true
for (( z = 1; z <= ${global_epochs}; z++ )); do
    for (( i = 1; i <= ${num_partitions}; i++ )); do
    echo "************************Training Partition ${i}************************"
    update_yaml_field "config_temp.yaml" "data_dir" "${data_dir}/par${i}/data.yaml"
    update_yaml_field "config_temp.yaml" "experiment" "${experiment}_par${i}"
    if [ "$initial" -eq 0 ]; then
        echo "Using config model..."
        initial=false
    else
        update_yaml_field "config_temp.yaml" "model" "./${project_train}/${experiment_train}/weights/last.pt"
    fi
    sh train.sh config_temp.yaml
    done
done
