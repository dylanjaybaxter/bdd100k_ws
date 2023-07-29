#!bin/bash
docker build -f ./Dockerfile \
    --build-arg dst="/app/dataset/1par_yolo_mots/" \
    --build-arg src="/app/dataset/bdd100k/" \
     -t processingimage .
docker run -v bdd100k-data:/app/dataset --gpus all \
    --ipc=host -it processingimage 