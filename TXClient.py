import basicvislib5549 as bvl
import ntlib
import src

import cv2
import numpy as np

'''
    TXClient is the client code that will run on the Jetson TX2.

    Upon initialization, presuming this is the main execution, it will run() in a loop until it is terminated.
    In other cases where running conditions are modified, it can exit given a condition.
'''


class TXClient(object):

    def __init__(self):

            self.Table = ntlib.ConnectTable()
            self.vis_init()
            self.isReset = False

    def vis_init(self):

        self.source = bvl.CamLib.cv_video_source('/dev/video1')
        ret, frame = self.source.read()

        y, h, x, w = frame.shape[0] / 5, frame.shape[0] / 5 * 3, frame.shape[1] / 5, frame.shape[1] / 5 * 3
        self.track_window = (x, y, w, h)

        self.angle = 90

        self.hsv_min = np.array([33, 80, 40])
        self.hsv_max = np.array([102, 255, 255])

        roi = frame[y:y + h, x:x + w]
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_roi, self.hsv_min, self.hsv_max)
        self.roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0, 180])
        cv2.normalize(self.roi_hist, self.roi_hist, 0, 255, cv2.NORM_MINMAX)

    def vis_reset(self):

        ret, frame = self.source.read()

        y, h, x, w = frame.shape[0] / 5, frame.shape[0] / 5 * 3, frame.shape[1] / 5, frame.shape[1] / 5 * 3
        self.track_window = (x, y, w, h)

    def run(self):

        """Single run only. Recommended for flexibility on termination."""

        if self.Table.Connected:
            self.Table.table.putBoolean("tableExists", True)

            if self.Table.table.getBoolean("VisionAssistanceEnabled", False) is True:
                self.track_window, self.angle = src.Src.vision_assistance(self.source, self.track_window, self.roi_hist)
                self.isReset = False

                self.Table.table.putNumber("Angle", self.angle)

            elif self.isReset is False and self.Table.table.getBoolean("VisionAssistanceEnabled", False) is False:
                self.vis_reset()
                self.isReset = True

    def test(self):

        """Test for connection and enabling"""

        if self.Table.Connected:
            self.Table.table.putBoolean("tableExists", True)

            if self.Table.table.getNumber("Number", 0) is 1:
                self.Table.table.putNumber("Number", 0)

    '''def looprun(self):

        """Run function looping itself."""

        while self.Table.Connected:
            self.Table.table.putBoolean("tableExists", True)

            if self.Table.table.getBoolean("Enabled", False) is True:

                # Put code here using 'src' package.
    '''

if __name__ == '__main__':
    TXC = TXClient()

    while True:
        TXC.run()