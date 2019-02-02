import basicvislib5549 as bvl
import math

class Src(object):

    @staticmethod
    def vision_assistance(source, window, roi_hist):

        trackwindow_new, pts = bvl.RobotVision.camshift_cv(source, window, roi_hist)

        camera_pitch = -45.0    #degrees estimate.
        height = 24             #inches estimate, not used.
        fov_factor = 1          #used to factor for the difference in field of view in cameras. Can be set to whatever.

        pitch_cos_val = math.cos(math.radians(camera_pitch))
        pitch_sin_val = math.sin(math.radians(camera_pitch))

        if pts is not False:
            for p in range(0, 4):
                if pts[p, 0] > source.shape[0]/2:
                    pts[p, 0] = pts[p, 0] - ((pts[p, 0] - source.shape[0]/2) * abs(pitch_sin_val) * fov_factor)

                elif pts[p, 0] < source.shape[0]/2:
                    pts[p, 0] = pts[p, 0] + ((pts[p, 0] - source.shape[0]/2) * abs(pitch_sin_val) * fov_factor)

                if pts[p, 1] < source.shape[1]/2:
                    pts[p, 1] = pts[p, 1] + ((pts[p, 1] - source.shape[1]/2) * abs(pitch_cos_val) * fov_factor)

                elif pts[p, 1] > source.shape[1]/2:
                    pts[p, 1] = pts[p, 1] - ((pts[p, 1] - source.shape[1]/2) * abs(pitch_cos_val) * fov_factor)

            for p in range(0, 4):

        #not complete here, under dev

        return trackwindow_new      #returns trackwindow as to keep evaluating for camshift each frame.