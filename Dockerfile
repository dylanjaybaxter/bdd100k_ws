FROM python:3.9

# Set Source and Destination
ARG dst="./"
ENV DST=$dst
ARG src="./"
ENV SRC=$src

# Set the working directory
WORKDIR /app

# Copy the Python script into the container
COPY proccess_data.py .

# Install OpenCV
RUN pip install opencv-python
RUN pip install pyyaml
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# Set the entry point
ENTRYPOINT python proccess_data.py --src $SRC --dst $DST
