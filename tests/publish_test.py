'''
This file contains a test for the im_publish library
'''
# Imports
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from im_publish.publish import ImageStreamer
import cv2 as cv
import threading

# Initialize Streamer
streamer = ImageStreamer(port=5000, debug=False)

# Capture frames from the webcam and continuously update the stream
cap = cv.VideoCapture(0)  # Use the default webcam (change the index if multiple webcams)
frame_count = 0
while True:
    ret, frame = cap.read()
    if ret:
        cv.imshow("Frame", frame)
        streamer.publish_frame(frame, f"Frame: {frame_count}\nLine 2")
    else:
        # In case of frame capture failure, handle appropriately (e.g., use a default image)
        # For example:
        # default_image = cv2.imread('path_to_default_image.jpg')
        # streamer.publish_image(default_image)
        print("Bad Image")
    if cv.waitKey(0) % 0xFF == ord('q'):
        cv.destroyAllWindows()
        break
    frame_count = frame_count + 1

