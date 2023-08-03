#!/bash/bin/

# Assign config path
config_path="$1"
# Check if the folder path is provided
if [ -z "$config_path" ]; then
  echo "Usage: $0 <config_path>"
  exit 1
fi

# Get evaluation parameters
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

# Update yaml fields because the way that ultralytics proccesses this is INSANE
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

# Update feilds in data.yaml with working dataset paths
update_yaml_field "${data_dir}/data.yaml" "train" "${data_dir}/train"
update_yaml_field "${data_dir}/data.yaml" "val" "${data_dir}/val"
update_yaml_field "${data_dir}/data.yaml" "test" "${data_dir}/test"

# Create file paths for model and project
exp_test_folder="${experiment_test}_test"
project_test_folder="${project_test}_test"
model_path="./${project_test}/${experiment_test}/weights/best.pt"


# Run the evaluation with parameters
yolo task=detect \
  mode=val \
  project=${project_test_folder} \
  name=${exp_test_folder} \
  model=${model_path} \
  data="datasets/${newfile}" \
  save_json=${save_json} \
  iou=${iou} \
  conf=${confidence} 2>&1 | tee output.txt

  mv output.txt ${project_test_folder}/${exp_test_folder}/


