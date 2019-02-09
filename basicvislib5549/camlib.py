import numpy as np
import cv2


class CamLib(object):
    class PlatformType:
        USB_CAM_LINUX = -1
        USB_CAM_WIN = -2
        JETSON_TX2_INT = -3

    class SourceType:
        CAMERA = 0
        VIDEO = 1
        IMAGE_ELSE = 2

    @staticmethod
    def cv_video_source(platform):
        """Gets a camera/video source.
        Args:
            platform: A PlatformType or a custom camera string.
        Returns:
            A VideoCapture object.
        """

        if platform is -1:

            try:
                camSrc = cv2.VideoCapture("/dev/video1")

            except:
                raise ("Error, Video source not found [USB_CAM_LINUX]")

        elif platform is -2:

            try:
                camSrc = cv2.VideoCapture(0)

            except:
                raise ("Error, Video source not found [USB_CAM_WIN]")

        elif platform is -3:

            try:
                camSrc = cv2.VideoCapture(
                    "nvcamerasrc ! video/x-raw(memory:NVMM), width=(int)640, height=(int)480, format=(string)I420, framerate=(fraction)30/1 ! nvvidconv flip-method=0 ! video/x-raw, format=(string)I420 ! videoconvert ! video/x-raw, format=(string)BGR ! appsink")

            except:
                raise ("Error, Video source not found [JETSON_TX2_INT]")

        else:

            try:
                camSrc = cv2.VideoCapture(platform)

            except:
                raise ("Error, Video source not found [Custom Input]")

        return camSrc

    @staticmethod
    def cv_display_source(videosrc, width, height, title, istype, **kwargs):
        """Displays a cv2.VideoCapture to a window.
        Args:
            videosrc: A source. Can be an image (imread) or video (VideoCapture).
            width: Width of video. 0 to automatically set width.
            height: Height of video. 0 to automatically set height.
            title: Title of window.
            istype: A SourceType representing whether the feed from the source is a video or a live feed.
            kwarg - keyexit: Value ID of keyboard key. If this value is True then the default key will be 'q'.
        Returns:
            A feed from the source in a new window.

        Note: If threading with display source, please use different source objects as inputs.
        """
        keyexit = kwargs.get('keyexit', True)

        if isinstance(videosrc, cv2.VideoCapture) is not True and istype is not 2:
            raise ("Error, object provided is not cv2.VideoCapture object")
        elif isinstance(videosrc, cv2.VideoCapture) is True and istype is 2:
            raise ("Error, expected image as source.")

        if isinstance(videosrc, cv2.VideoCapture) is True:

            if width is 0:
                width = int(videosrc.get(3))

            if height is 0:
                height = int(videosrc.get(4))
        elif isinstance(videosrc, np.ndarray) is True:

            if width is 0:
                width = int(videosrc.shape[1])

            if height is 0:
                height = int(videosrc.shape[0])


        if (keyexit is True) or (keyexit is False and istype is 2):
            keyexit = 'q'

        if istype is 0:
            fps = 10
        elif istype is 1:
            fps = int(videosrc.get(cv2.CAP_PROP_FPS)) * 10

        windowName = "cv2WindowDisplay"
        cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(windowName, width, height)
        cv2.setWindowTitle(windowName, title)

        if istype is not 2:

            while videosrc.isOpened():

                if cv2.getWindowProperty(windowName, 0) < 0:
                    videosrc.release()
                ret, frame = videosrc.read()
                cv2.imshow(windowName, frame)
                if keyexit is not False:
                    if cv2.waitKey(100) & 0xFF is ord(keyexit):
                        cv2.destroyWindow(windowName)
                        videosrc.release()

                cv2.waitKey(fps)

        elif istype is 2 and isinstance(videosrc, np.ndarray) is True:
            cv2.imshow(windowName, videosrc)
            if cv2.waitKey(0) & 0xFF is ord(keyexit):
                cv2.destroyWindow(windowName)

    @staticmethod
    def cv_write_video_stream(videosrc, width, height, videoname, keyexit):
        """Displays a cv2.VideoCapture to a window.
                Args:
                    videosrc: A VideoCapture object.
                    width: Video width. 0 to set automatically.
                    height: Video height. 0 to set automatically.
                    videoname: Name of video file to be output.
                    keyexit: Value ID of keyboard key.
                Returns:
                    No values, runs stream to file until key is pressed.
                """
        if isinstance(videosrc, cv2.VideoCapture) is not True:
            raise ("Error, video source provided is not a cv2.VideoCapture")

        if width is 0:
            width = int(videosrc.get(3))

        if height is 0:
            height = int(videosrc.get(4))

        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter('%s.avi' % videoname, fourcc, 30, (width, height))

        while True:
            ret, frame = videosrc.read()
            if ret is True:
                out.write(frame)
                if cv2.waitKey(1) & 0xFF is ord(keyexit):
                    break

            else:
                break

        videosrc.release()
        out.release()