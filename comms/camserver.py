import cv2
import numpy
import cscore

class VideoStream(object):

    def __init__(self):

        self.cameraserv = cscore.CameraServer()
        self.vsink = self.cameraserv.addServer("DS")
        self.source = self.cameraserv.putVideo("localhost", 280, 210)
        self.vsink.setSource(self.source)



    def putFrame(self, cv_frame):

        self.source.putFrame()