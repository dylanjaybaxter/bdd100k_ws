docker build -f ./yolo_training/Dockerfile \
     -t trainingimage .
docker run -v bdd100k-data:/workspace/dataset \
     --gpus all \
     --build-arg UID_VAR=$(id -u) \
     --build-arg GID_VAR=$(id -g) \
     --ipc=host -it trainingimage 