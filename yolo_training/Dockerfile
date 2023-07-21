#Using Pytorch/CUDA Docker
FROM pytorch/pytorch:1.7.0-cuda11.0-cudnn8-devel

# Import Requirements
RUN pip install --upgrade pip
RUN pip install ultralytics
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys A4B469963BF863CC
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install opencv-python

# Setup Work Directory
WORKDIR /workspace

# Copy Files to Working Directory
COPY . /workspace

# When started run the training
CMD sh run.sh config.yaml
