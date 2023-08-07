#Using Pytorch/CUDA Docker
FROM ultralytics/ultralytics

# Set environment variables for UID and GID
ARG UID_VAR=1000
ARG GID_VAR=1000

# Import Requirements
RUN pip install --upgrade pip
RUN pip install ultralytics
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys A4B469963BF863CC
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install opencv-python

# Setup Work Directory
WORKDIR /workspace

# Copy Files to Working Directory
COPY . /workspace

# When started, run the training
CMD sh eval.sh config.yaml
