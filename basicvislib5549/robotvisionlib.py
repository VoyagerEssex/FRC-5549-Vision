import numpy as np
import cv2
import imutils


class RobotVision(object):
    class BlurType:
        BOX_BLUR = 1
        GAUSSIAN_BLUR = 2
        MEDIAN_FILTER = 3

    class FlipMode:
        HORIZONTAL = 0
        VERTICAL = 1
        BOTH = -1

    @staticmethod
    def rotate_image(input, rotation, flip):
        """
        :param input: A numpy.ndarray
        :param rotation: Degrees of rotation, including 90, -90 degrees and full flipping.
        :param flip: Mode of flipping.
        :return: A rotated frame
        """
        if flip is not False:
            input = cv2.flip(input, flip)

        rotated = imutils.rotate(input, rotation)

        return rotated

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
        :param input: Input frame.
        :param hue: Input array for min-max hue.
        :param sat: Input array for min-max sat.
        :param val: Input array for min-max val.
        :param window: window for meanShift to locate in.
        :return: Bounding box (and new window), center of the evaluated meanshift.
        """

        track_window = window

        term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)

        hsv = cv2.cvtColor(input, cv2.COLOR_BGR2HSV)
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
        :param window: window for CamShift to locate in.
        :param roi_hist: Input mask for camshift.
        :return: Bounding box (and new window) and points of the evaluated CamShift.
        """

        track_window = window

        term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)

        hsv = cv2.cvtColor(input, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)
        # apply meanshift to get the new location
        rect, track_window = cv2.CamShift(dst, track_window, term_crit)
        # give points
        pts = cv2.boxPoints(rect)
        pts = np.int0(pts)
        x, y, w, h = track_window

        return (x, y, w, h), pts

    @staticmethod
    def brightness_contrast(frame, brightness, contrast):
        """
        :param frame: Input frame for brightness and contrast
        :param brightness: Brightness value
        :param contrast: Contrast value
        :return: Frame processed by contrast and brightness operations
        """

        frame = np.int16(frame)
        frame = frame * (contrast / 127 + 1) - contrast + brightness
        frame = np.clip(frame, 0, 255)
        frame = np.uint8(frame)

        return frame