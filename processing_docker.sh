#!bin/bash
docker build -f ./Dockerfile -t processingimage .
docker run -v bdd100k-data:/app/dataset --gpus all /
    --build-arg dst="/app/dataset/1par_yolo_mots/" /
    --build-arg src="/app/dataset/bdd100k/"
     --ipc=host -it processingimage 