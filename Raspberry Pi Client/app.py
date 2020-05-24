#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response

# OpenCV camera module (requires picamera package)
from camera_opencv import Camera

#Server communication
import cv2
from urllib.request import urlopen
import requests
import numpy as np

app = Flask(__name__,
            static_url_path='', 
            static_folder='web/static',
            template_folder='web/templates')


@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/prototype')
def prototype():
    """Video streaming home page."""
    status = ""
    plaque = ""
    loss = ""
    crack = ""
    caries = ""
    return render_template('prototype.html', status=status, plaque=plaque, loss=loss, crack=crack, caries=caries)


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/post/", methods=['POST'])
def post():
    # Value
    status = "Failed"
    plaque = ""
    loss = ""
    crack = ""
    caries = ""

    # Save current frame
    filename = '/home/pi/playground/captured/capture.jpeg'
    _bytes = bytes()
    stream = urlopen('http://0.0.0.0:5000/video_feed')
    while True:
        _bytes += stream.read(1024)
        a = _bytes.find(b'\xff\xd8')
        b = _bytes.find(b'\xff\xd9')
        if a != -1 and b != -1:
            jpg = _bytes[a:b+2]
            _bytes = _bytes[b+2:]
            i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            cv2.imwrite(filename, i)
            break

    # Post to the server
    image = open(filename, 'rb').read()
    r = requests.post('http://'+URL+'/predict', files={"image":image}).json()
    if r["success"]:
        pred = r["result"]

        plaque = pred["Dental Plaque"]
        loss = pred["Tooth Loss"]
        crack = pred["Cracked Teeth"]
        caries = pred["Dental Caries"]
    
    return render_template('prototype.html', status=status, plaque=plaque, loss=loss, crack=crack, caries=caries)

if __name__ == '__main__':
    URL = input()
    app.run(host='0.0.0.0', threaded=True)
