docker build -f ./yolo_eval/Dockerfile \
     --build-arg UID_VAR=$(id -u) \
     --build-arg GID_VAR=$(id -g) \
     -t evalimage .
docker run -v bdd100k-data:/workspace/dataset \
     --gpus all \
     --ipc=host -it evalimage 