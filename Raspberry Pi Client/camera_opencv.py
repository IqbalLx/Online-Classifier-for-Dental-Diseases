import os
import cv2
from base_camera import BaseCamera


class Camera(BaseCamera):
    video_source = 0

    def __init__(self):
        # if os.environ.get('OPENCV_CAMERA_SOURCE'):
        #    Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        
        super(Camera, self).__init__()

    # @staticmethod
    # def set_video_source(source):
    #    Camera.video_source = source

    @staticmethod
    def frames():
        cam = cv2.VideoCapture(Camera.video_source)
        if not cam.isOpened():
            raise RuntimeError('Could not start camera.')
        
        init_width = cam.get(3)
        init_height = cam.get(4)
        
        width = 500
        ratio = width / init_width
        height = int(init_height*ratio)
        #print(width, height)
        
        while True:
            # read current frame
            _, img = cam.read()
            
            img = cv2.resize(img, (width, height), interpolation=cv2.INTER_LINEAR)
            
            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()
