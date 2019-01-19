import numpy as np
import cv2


class CamLib(object):
    class PlatformType:
        USB_CAM_LINUX = 1
        USB_CAM_WIN = 2
        JETSON_TX2_INT = 3

    @staticmethod
    def cv_video_source(platform):
        """Gets a camera/video source.
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
                raise ("Error, Video source not found [USB_CAM_LINUX]")

        elif platform is 2:

            try:
                global camSrc
                camSrc = cv2.VideoCapture(0)

            except:
                raise ("Error, Video source not found [USB_CAM_WIN]")

        elif platform is 3:

            try:
                global camSrc
                camSrc = cv2.VideoCapture(
                    "nvcamerasrc ! video/x-raw(memory:NVMM), width=(int)640, height=(int)480, format=(string)I420, framerate=(fraction)30/1 ! nvvidconv flip-method=0 ! video/x-raw, format=(string)I420 ! videoconvert ! video/x-raw, format=(string)BGR ! appsink")

            except:
                raise ("Error, Video source not found [JETSON_TX2_INT]")

        else:

            try:
                global camSrc
                camSrc = cv2.VideoCapture(platform)

            except:
                raise ("Error, Video source not found [Custom Input]")

        return camSrc

    @staticmethod
    def cv_display_source(videosrc, width, height, title, **kwargs):
        """Displays a cv2.VideoCapture to a window.
        Args:
            videosrc: A VideoCapture object.
            width: Width of video.
            height: Height of video.
            title: Title of window.
            kwarg - keyExit: Value ID of keyboard key. If this value is True then the default key will be 'q'.
        Returns:
            A video feed from the VideoCapture in a new window.
        """
        keyexit = kwargs.get('keyExit', False)

        if keyexit is type(bool) and keyexit is True:
            keyexit = ord('q')

        if type(videosrc) is not cv2.VideoCapture:
            raise ("Error, object provided is not cv2.VideoCapture object")

        windowName = "cv2WindowDisplay"
        cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(windowName, width, height)
        cv2.setWindowTitle(windowName, title)

        while videosrc.isOpened():

            if cv2.getWindowProperty(windowName, 0) < 0:
                break
            ret, frame = videosrc.read()
            cv2.imshow(windowName, frame)
            if cv2.waitKey(10) & 0xFF is ord(keyexit) and keyexit is True:
                break

            cv2.waitKey(10)

    @staticmethod
    def cv_write_video_stream(videosrc, width, height, videoname, keyexit):
        """Displays a cv2.VideoCapture to a window.
                Args:
                    videosrc: A VideoCapture object.
                    width: Video width.
                    height: Video height.
                    videoname: Name of video file to be output.
                    keyexit: Value ID of keyboard key.
                Returns:
                    No values, runs stream to file until key is pressed.
                """
        fourcc = cv2.VideoWriter_fourcc(*'X264')
        out = cv2.VideoWriter('%s.avi' % videoname, fourcc, 30, (width, height), True)

        while videosrc.isOpened():
            ret, frame = videosrc.read()
            if ret is True:
                out.write(frame)
                if cv2.waitKey(1) & 0xFF is ord(keyexit):
                    break

            else:
                break

        videosrc.release()
        out.release()
