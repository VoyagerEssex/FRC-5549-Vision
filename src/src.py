from basicvislib5549 import robotvisionlib as bvl
import cv2
import math

class Src(object):

    @staticmethod
    def vision_assistance_contour(source):

        source = bvl.RobotVision.resize_image(source, 280, 210, cv2.INTER_CUBIC)

        source = bvl.RobotVision.blur(source, bvl.RobotVision.BlurType.BOX_BLUR, 5)

        source = bvl.RobotVision.hsv_threshold(source, [64, 88], [89, 255], [0, 255])

        contours = bvl.RobotVision.find_contours(source, False)

        contours = bvl.RobotVision.filter_contours(contours, 200, 0, 10, 1000, 10, 1000, [0, 100], 100000, 0, 0, 1000)

        contours = bvl.RobotVision.convex_hulls(contours)

        bboxes = bvl.RobotVision.contour_bounding_box(contours)

        centers = bvl.RobotVision.contour_centers(contours)

        avgcenx = 0
        avgceny = 0

        for c in contours:
            avgcenx = avgcenx + centers[c, 0]
            avgceny = avgceny + centers[c, 1]

        return (avgcenx, avgceny), centers, bboxes


    @staticmethod
    def vision_assistance_camshift(source, window, roi_hist):

        trackwindow_new, pts = bvl.RobotVision.camshift_cv(source, window, roi_hist)

        angle = 0

        if pts is not False:
            # magnitude = math.sqrt(math.pow((pts[1, 0] - pts[0, 0]), 2) + math.pow((pts[1, 1] - pts[0, 1]), 2))
            ymag1 = (pts[1, 0] - pts[0, 0])
            xmag1 = (pts[1, 1] - pts[0, 1])

            ymag2 = (pts[2, 0] - pts[1, 0])
            xmag2 = (pts[2, 1] - pts[1, 1])

            angle = 90

            angle1 = (abs(math.degrees(math.atan(ymag1 / xmag1)) - 180))
            angle2 = (abs(math.degrees(math.atan(ymag2 / xmag2)) - 180))

            if 45 < angle1 < 135:
                angle = angle1

            if 45 < angle2 < 135:
                angle = angle2

        return trackwindow_new, angle      #returns trackwindow as to keep evaluating for camshift each frame, angle as evaluated angle.