docker build -f ./yolo_training/Dockerfile \
     --build-arg UID_VAR=$(id -u) \
     --build-arg GID_VAR=$(id -g) \
     -t trainingimage .
docker run -v bdd100k-data:/workspace/dataset \
     --gpus all \
     --ipc=host trainingimage 