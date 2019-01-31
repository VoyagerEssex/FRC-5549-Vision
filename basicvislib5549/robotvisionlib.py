import numpy as np
import cv2


class RobotVision(object):
    class BlurType:
        BOX_BLUR = 1
        GAUSSIAN_BLUR = 2
        MEDIAN_FILTER = 3

    @staticmethod
    def resize_image(input, width, height, interpolation):
        """Scales and image to an exact size.
        Args:
            input: A numpy.ndarray.
            width: The desired width in pixels.
            height: The desired height in pixels.
            interpolation: Opencv enum for the type of interpolation.
        Returns:
            A numpy.ndarray of the new size.
        """
        return cv2.resize(input, ((int)(width), (int)(height)), 0, 0, interpolation)

    @staticmethod
    def blur(src, method, radius):
        """Softens an image using one of several filters.
        Args:
            src: The source mat (numpy.ndarray).
            method: The BlurType to perform represented as an int.
            radius: The radius for the blur as a float.
        Returns:
            A numpy.ndarray that has been blurred.
        """
        if (method is 1):
            ksize = int(2 * round(radius) + 1)
            return cv2.blur(src, (ksize, ksize))
        elif (method is 2):
            ksize = int(6 * round(radius) + 1)
            return cv2.GaussianBlur(src, (ksize, ksize), round(radius))
        elif (method is 3):
            ksize = int(2 * round(radius) + 1)
            return cv2.medianBlur(src, ksize)
        else:
            return cv2.bilateralFilter(src, -1, round(radius), round(radius))

    @staticmethod
    def hsv_threshold(input, hue, sat, val):
        """Segment an image based on hue, saturation, and value ranges.
        Args:
            input: A BGR numpy.ndarray.
            hue: A list of two numbers the are the min and max hue.
            sat: A list of two numbers the are the min and max saturation.
            val: A list of two numbers the are the min and max value.
        Returns:
            A black and white numpy.ndarray.
        """
        out = cv2.cvtColor(input, cv2.COLOR_BGR2HSV)
        return cv2.inRange(out, (hue[0], sat[0], val[0]), (hue[1], sat[1], val[1]))

    @staticmethod
    def find_contours(input, external_only):
        """Sets the values of pixels in a binary image to their distance to the nearest black pixel.
        Args:
            input: A numpy.ndarray.
            external_only: A boolean. If true only external contours are found.
        Return:
            A list of numpy.ndarray where each one represents a contour.
        """
        if (external_only):
            mode = cv2.RETR_EXTERNAL
        else:
            mode = cv2.RETR_LIST
        method = cv2.CHAIN_APPROX_SIMPLE
        im2, contours, hierarchy = cv2.findContours(input, mode=mode, method=method)
        return contours

    @staticmethod
    def filter_contours(input_contours, min_area, min_perimeter, min_width, max_width,
                        min_height, max_height, solidity, max_vertex_count, min_vertex_count,
                        min_ratio, max_ratio):
        """Filters out contours that do not meet certain criteria.
        Args:
            input_contours: Contours as a list of numpy.ndarray.
            min_area: The minimum area of a contour that will be kept.
            min_perimeter: The minimum perimeter of a contour that will be kept.
            min_width: Minimum width of a contour.
            max_width: MaxWidth maximum width.
            min_height: Minimum height.
            max_height: Maximimum height.
            solidity: The minimum and maximum solidity of a contour.
            min_vertex_count: Minimum vertex Count of the contours.
            max_vertex_count: Maximum vertex Count.
            min_ratio: Minimum ratio of width to height.
            max_ratio: Maximum ratio of width to height.
        Returns:
            Contours as a list of numpy.ndarray.
        """
        output = []
        for contour in input_contours:
            x, y, w, h = cv2.boundingRect(contour)
            if (w < min_width or w > max_width):
                continue
            if (h < min_height or h > max_height):
                continue
            area = cv2.contourArea(contour)
            if (area < min_area):
                continue
            if (cv2.arcLength(contour, True) < min_perimeter):
                continue
            hull = cv2.convexHull(contour)
            solid = 100 * area / cv2.contourArea(hull)
            if (solid < solidity[0] or solid > solidity[1]):
                continue
            if (len(contour) < min_vertex_count or len(contour) > max_vertex_count):
                continue
            ratio = (float)(w) / h
            if (ratio < min_ratio or ratio > max_ratio):
                continue
            output.append(contour)
        return output

    @staticmethod
    def convex_hulls(input_contours):
        """Computes the convex hulls of contours.
        Args:
            input_contours: A list of numpy.ndarray that each represent a contour.
        Returns:
            A list of numpy.ndarray that each represent a contour.
        """
        output = []
        for contour in input_contours:
            output.append(cv2.convexHull(contour))
        return output

    @staticmethod
    def contour_centers(input_contours):
        """Computes the convex hulls of contours.
        Args:
            input_contours: A list of numpy.ndarray that each represent a contour.
        Returns:
            A list of cartesian coordinates representing the center of contours.
        """
        output = []
        for c in input_contours:
            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            output.append([cX, cY])

        return output

    @staticmethod
    def contour_bounding_box(input_contours):
        """Computes the convex hulls of contours.
        Args:
            input_contours: A list of numpy.ndarray that each represent a contour.
        Returns:
            A list of coordinates X and Y (From top-left), dimensions width and height for each contour.
        """
        output = []
        for c in input_contours:
            x, y, w, h = cv2.boundingRect(c)
            output.append([x, y, w, h])

        return output

    @staticmethod
    def meanshift_cv(input, window, roi_hist):
        """
        :param input: Input video source.
        :param hue: Input array for min-max hue.
        :param sat: Input array for min-max sat.
        :param val: Input array for min-max val.
        :param window: window for meanShift to locate in.
        :return: Bounding box (and new window), center of the evaluated meanshift.
        """
        ret, frame = input.read()

        track_window = window

        term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)

        if ret == True:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            dst = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)
            # apply meanshift to get the new location
            ret, track_window = cv2.meanShift(dst, track_window, term_crit)
            # give dimensions
            x, y, w, h = track_window

        return (x, y, w, h), ((w/2)+x, (h/2)+y)

    @staticmethod
    def camshift_cv(input, window, roi_hist):
        """
        :param input: Input video source.
        :param hue: Input array for min-max hue.
        :param sat: Input array for min-max sat.
        :param val: Input array for min-max val.
        :param window: window for CamShift to locate in.
        :return: Bounding box (and new window) and points of the evaluated CamShift.
        """
        ret, frame = input.read()

        track_window = window

        term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)

        if ret == True:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            dst = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)
            # apply meanshift to get the new location
            rect, track_window = cv2.CamShift(dst, track_window, term_crit)
            # give points
            pts = cv2.boxPoints(rect)
            pts = np.int0(pts)
            x, y, w, h = track_window

        return (x, y, w, h), pts


class CamLib(object):
    class PlatformType:
        USB_CAM_LINUX = 1
        USB_CAM_WIN = 2
        JETSON_TX2_INT = 3

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

        if platform is 1:

            try:
                camSrc = cv2.VideoCapture("/dev/video1")

            except:
                raise ("Error, Video source not found [USB_CAM_LINUX]")

        elif platform is 2:

            try:
                camSrc = cv2.VideoCapture(0)

            except:
                raise ("Error, Video source not found [USB_CAM_WIN]")

        elif platform is 3:

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
