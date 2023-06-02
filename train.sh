# !/bin/bash

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

eval $(parse_yaml config.yaml)

cd ${data_dir}
data_path=$(pwd)
# Create a Copy of data.yaml for evaluating the test
newfile="data_train.yaml"
if [ -e $newfile ]; then
    echo "Training Data Found."
fi
field="train"
new_value="${data_path}/train/images"
file_contents=$(cat data.yaml)
# Replace the old value with the new value
new_contents="$(echo "$file_contents" | sed -e "s@^${field}:.*@${field}: ${new_value}@")"
echo "$new_contents" > $newfile

field="val"
new_value="${data_path}/valid/images"
file_contents=$(cat ${newfile})
# Replace the old value with the new value
new_contents="$(echo "$file_contents" | sed -e "s@^${field}:.*@${field}: ${new_value}@")"
echo "$new_contents" > $newfile

field="test"
new_value="${data_path}/test/images"
file_contents=$(cat ${newfile})
# Replace the old value with the new value
new_contents="$(echo "$file_contents" | sed -e "s@^${field}:.*@${field}: ${new_value}@")"

# Write the new contents back to the file
echo "$new_contents" > $newfile

# Run the Training Script
touch /mpac/TRAINING_IN_PROGRESS.txt
cd ..
yolo task=detect \
  mode=train \
  model=$model \
  project=$project_train \
  name=$experiment_train \
  data="datasets/${newfile}" \
  epochs=$epochs \
  imgsz=$im_size \
  batch=$batch \
  patience=$patience \
  device=$device \
  workers=$workers \
  exist_ok=$overwrite \
  lr0=$lr0 \
  lrf=$lrf \
  momentum=$momentum \
  weight_decay=$weight_decay \
  warmup_epochs=$warmup \
  warmup_momentum=$warmup_momentum \
  warmup_bias_lr=$warmup_bias_lr \
  box=$box \
  cls=$cls \
  dfl=$dfl \
  fl_gamma=$fl_gamma \
  label_smoothing=$label_smoothing \
  nbs=$nbs \
  2>&1 

  rm /mpac/TRAINING_IN_PROGRESS.txt
