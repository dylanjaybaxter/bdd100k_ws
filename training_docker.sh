docker build -f ./yolo_training/Dockerfile \
     -t trainingimage .
docker run -v bdd100k-data:/app/dataset --gpus all \
    --ipc=host -it trainingimage 