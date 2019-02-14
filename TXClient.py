import basicvislib5549 as bvl
import comms
import src
import math

import numpy as np

'''
    TXClient is the client code that will run on the Jetson TX2.

    Upon initialization, presuming this is the main execution, it will run() in a loop until it is terminated.
    In other cases where running conditions are modified, it can exit given a condition.
'''


class TXClient(object):

    def __init__(self):

        self.Table = comms.ConnectTable()
        self.isReset = False
        self.vidstream = comms.VideoStream()

        while self.Table.Connected:
            self.Table.table.putBoolean("tableExists", True)

            if self.Table.table.getNumber("Mode", -1) is 0:
                self.test()

            elif self.Table.table.getNumber("Mode", -1) is 1:
                self.run()
                self.vissource = bvl.CamLib.cv_video_source('/dev/video1')

                self.avg_centers = []
                self.all_centers = []
                self.contour_dimensions = []

            elif self.Table.table.getNumber("Mode", -1) is 2:
                self.dualrun()
                self.lvissource = bvl.CamLib.cv_video_source('/dev/video1')
                self.rvissource = bvl.CamLib.cv_video_source('/dev/video2')

                self.lavg_centers = []
                self.lall_centers = []
                self.lcontour_dimensions = []
                self.ravg_centers = []
                self.rall_centers = []
                self.rcontour_dimensions = []


    def vis_reset(self):

        """Method to reset variables after finishing loop and be ready for enabling. Reset code goes here."""

        return

    def dualrun(self):

        if self.Table.table.getBoolean("Enabled", False) is True:
            lret, lsource = self.lvissource.read()
            rret, rsource = self.rvissource.read()
            self.lavg_centers, self.lall_centers, self.lcontour_dimensions = src.Src.vision_assistance_contour(lsource)
            self.ravg_centers, self.rall_centers, self.rcontour_dimensions = src.Src.vision_assistance_contour(rsource)
            self.isReset = False

            lcwidth = abs(self.lcontour_dimensions[1, 0] - (self.lcontour_dimensions[0, 0] + self.lcontour_dimensions[0, 2]))
            lcenterdist = (lsource.shape[1]-self.avg_centers)
            lrundist = (lcenterdist*14) / lcwidth
            loffset_direction = math.degrees(math.atan(lrundist/lcenterdist))

            rcwidth = abs(self.rcontour_dimensions[1, 0] - (self.rcontour_dimensions[0, 0] + self.rcontour_dimensions[0, 2]))
            rcenterdist = (rsource.shape[1] - self.avg_centers)
            rrundist = (rcenterdist * 14) / rcwidth
            roffset_direction = math.degrees(math.atan(rrundist / rcenterdist))

            self.Table.table.putNumber("Left Camera Direction", loffset_direction)
            self.Table.table.putNumber("Left Camera Direction", roffset_direction)

            self.vidstream.putFrame(rsource)

        elif self.isReset is False and self.Table.table.getBoolean("Enabled", False) is False:
            self.vis_reset()
            self.isReset = True

    def run(self):

        """Single run only. Recommended for flexibility on termination."""

        if self.Table.table.getBoolean("Enabled", False) is True:
            ret, source = self.vissource.read()
            self.avg_centers, self.all_centers, self.contour_dimensions = src.Src.vision_assistance_contour(source)
            self.isReset = False

            cwidth = abs(self.contour_dimensions[1, 0] - (self.contour_dimensions[0, 0] + self.contour_dimensions[0, 2]))
            centerdist = (source.shape[1]-self.avg_centers)
            rundist = (centerdist*14) / cwidth
            offset_direction = math.degrees(math.atan(rundist/centerdist))

            self.Table.table.putNumberArray("contour centers", self.avg_centers)
            self.Table.table.putNumberArray("all visible contour centers", self.all_centers)
            self.Table.table.putNumberArray("all contour dimensions", self.contour_dimensions)
            self.Table.table.putNumber("Direction", offset_direction)

            self.vidstream.putFrame(source)

        elif self.isReset is False and self.Table.table.getBoolean("Enabled", False) is False:
            self.vis_reset()
            self.isReset = True

    def test(self):

        """Test for connection and enabling"""
        if self.Table.table.getBoolean("Enabled", False) is True:
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
