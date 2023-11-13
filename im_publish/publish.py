import cv2 as cv
import numpy as np
from flask import Flask, render_template, Response, jsonify
import threading
import logging, sys

class ImageStreamer:
    '''
    Class: Image Streamer
    Desc: Streams an image to a local port
    Usage:
    TBI
    '''
    def __init__(self, port, debug=False):
        # Initialize Frame
        fbuf = np.zeros((480, 640, 3), dtype=np.uint8)
        ret, frame_buffer = cv.imencode('.jpg', fbuf)
        # Set Description
        self.desc = ""
        self.data = {'frame':frame_buffer.tobytes(), 'desc':self.desc}
        # Setup App
        self.app = Flask(__name__, template_folder='templates')
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/video_feed', 'video_feed', self.video_feed_route)
        self.app.add_url_rule('/description', 'description', self.get_description)
        self.app.debug = debug
        if debug:
            self.app.logger.addHandler(logging.StreamHandler(sys.stdout))
        else:
            log = logging.getLogger('werkzeug')
            log.setLevel(logging.ERROR)
        # Run Server in New Thread
        self.port = port
        self.thread = threading.Thread(target=self.app.run, kwargs={'host': '0.0.0.0', 'port': port, 'debug': debug, 'use_reloader':False})
        self.thread.setDaemon(True)
        self.thread.start()
        self.running = True
        

    def publish_frame(self, im=None, desc=''):
        if im is not None:
            ret, buffer = cv.imencode('.jpg', im)
            self.data = {'frame':buffer.tobytes(), 'desc':desc}
    
    def video_feed_route(self):
        def generate():
            while self.running:
                yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + self.data['frame'] + b'\r\n' +
                           b'<p>' + self.data['desc'].encode('utf-8') + b'</p>\r\n')
        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
        
    def index(self):
        return render_template('index.html')
    
    def get_description(self):
        return self.data['desc']
    
    def run_server(self):
        self.app.run(host='0.0.0.0', port=self.port, debug=True, use_reloader=False)
