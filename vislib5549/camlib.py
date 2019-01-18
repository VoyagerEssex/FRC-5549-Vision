import numpy as np
import cv2

class CamLib(object):

    class PlatformType:
        USB_CAM_LINUX = 1
        USB_CAM_WIN = 2
        JETSON_TX2_INT = 3

    @staticmethod
    def cv_camera_source(platform):
        """Scales and image to an exact size.
        Args:
            platform: A PlatformType or a custom camera string.
        Returns:
            A VideoCapture object.
        """
        camSrc = 0

        if platform is 1:

            try:
                global camSrc
                camSrc = cv2.VideoCapture("/dev/video1")

            except:
                raise ("Error, Camera not found [USB_CAM_LINUX]")

        elif platform is 2:

            try:
                global camSrc
                camSrc = cv2.VideoCapture(0)

            except:
                raise ("Error, Camera not found [USB_CAM_WIN]")

        elif platform is 3:

            try:
                global camSrc
                camSrc = cv2.VideoCapture("nvcamerasrc ! video/x-raw(memory:NVMM), width=(int)640, height=(int)480, format=(string)I420, framerate=(fraction)30/1 ! nvvidconv flip-method=0 ! video/x-raw, format=(string)I420 ! videoconvert ! video/x-raw, format=(string)BGR ! appsink")

            except:
                raise ("Error, Camera not found [JETSON_TX2_INT]")

        else:

            try:
                global camSrc
                camSrc = cv2.VideoCapture(platform)

            except:
                raise("Error, Camera not found [Custom Input]")

        return camSrc

    @staticmethod
    def cv_display_capture(videoSrc, width, height, title):
        """Scales and image to an exact size.
        Args:
            videoSrc: A VideoCapture object.
            width: Width of video.
            height: Height of video.
            title: Title of window.
        Returns:
            A video feed from the VideoCapture in a new window.
        """
        if type(videoSrc) is not cv2.VideoCapture:
            raise ("Error, object provided is not cv2.VideoCapture object")

        windowName = "cv2WindowsDisplay"
        cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(windowName, width, height)
        cv2.setWindowTitle(windowName, title)

        while True:

            if cv2.getWindowProperty(windowName, 0) < 0:
                break
            ret, frame = videoSrc.read()
            cv2.imshow(windowName, frame)
            cv2.waitKey(10)