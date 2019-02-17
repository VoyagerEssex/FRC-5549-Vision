import basicvislib5549 as bvl
import comms
import src

import math

import traceback
import numpy as np

'''
    TXClient is the client code that will run on the Jetson TX2.

    Upon initialization, presuming this is the main execution, it will run in a loop given an 'Enabled' and 'Mode'
    key from SmartDashboard until it is terminated.
    
    Keys that should be established in SmartDashboard to control operations:
        Enabled: True or False, should be set in SmartDashboard when a button is pressed, this key enables
            running the modes.
        Mode: May be set to a number inclusive of the range -1 to 2. (1 runs with single camera, 2 runs with two.)
        CameraStream: Should be set to True if using a camera on the robot.
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
                try:
                    self.vissource

                except NameError:
                    self.vissource = bvl.CamLib.cv_video_source('/dev/video1')

                self.run()

                self.avg_centers = []
                self.all_centers = []
                self.contour_dimensions = []

            elif self.Table.table.getNumber("Mode", -1) is 2:
                try:
                    self.lvissource

                except NameError:
                    self.lvissource = bvl.CamLib.cv_video_source('/dev/video1')

                try:
                    self.rvissource

                except NameError:
                    self.rvissource = bvl.CamLib.cv_video_source('/dev/video2')

                else:
                    self.dualrun()

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

            if len(self.lcontour_dimensions) > 1:
                self.lcwidth = abs(self.lcontour_dimensions[1, 1] - (self.lcontour_dimensions[0, 1] + self.lcontour_dimensions[0, 3]))

            elif len(self.lcontour_dimensions) == 1:
                self.lcwidth = self.lcontour_dimensions[0, 3]

            lcenterdist = -(lsource.shape[0]/2 - self.lavg_centers)
            lhypodist = (lcenterdist*3.5) / self.lcwidth
            loffset_direction = math.degrees(math.atan(lhypodist / lcenterdist))

            if len(self.rcontour_dimensions) > 1:
                self.rcwidth = abs(self.rcontour_dimensions[1, 1] - (self.rcontour_dimensions[0, 1] + self.rcontour_dimensions[0, 3]))

            elif len(self.rcontour_dimensions) == 1:
                self.rcwidth = self.rcontour_dimensions[0, 3]

            rcenterdist = -(rsource.shape[0]/2 - self.ravg_centers)
            rhypodist = (rcenterdist * 3.5) / self.rcwidth
            roffset_direction = math.degrees(math.atan(rhypodist / rcenterdist))

            self.Table.table.putNumber("Left Camera Direction", loffset_direction)
            self.Table.table.putNumber("Right Camera Direction", roffset_direction)
            self.Table.table.putNumber("Left Camera Distance", lhypodist)
            self.Table.table.putNumber("Right Camera Distance", rhypodist)

            if self.Table.table.getBoolean("CameraStream", False) is True:
                self.vidstream.putFrame(lsource)

        elif self.isReset is False and self.Table.table.getBoolean("Enabled", False) is False:
            self.vis_reset()
            self.isReset = True

    def run(self):

        """Single run only. Recommended for flexibility on termination."""

        if self.Table.table.getBoolean("Enabled", False) is True:
            ret, source = self.vissource.read()
            self.avg_centers, self.all_centers, self.contour_dimensions = src.Src.vision_assistance_contour(source)
            self.isReset = False

            if len(self.contour_dimensions) > 1:
                self.cwidth = abs(self.contour_dimensions[1, 1] - (self.contour_dimensions[0, 1] + self.contour_dimensions[0, 3]))

            elif len(self.contour_dimensions) == 1:
                self.cwidth = self.contour_dimensions[0, 3]

            centerdist = (source.shape[0]/2-self.avg_centers)
            hypodist = (centerdist*3.5) / self.cwidth
            offset_direction = math.degrees(math.atan(hypodist/centerdist))

            self.Table.table.putNumberArray("contour centers", self.avg_centers)
            self.Table.table.putNumberArray("all visible contour centers", self.all_centers)
            self.Table.table.putNumberArray("all contour dimensions", self.contour_dimensions)
            self.Table.table.putNumber("Direction", offset_direction)
            self.Table.table.putNumber("Camera Distance", hypodist)

            if self.Table.table.getBoolean("CameraStream", False) is True:
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
    try:
        TXC = TXClient()
    except Exception as e:
        with open('txclientlog.txt', 'w') as f:
            f.write(str(e))
            f.write(traceback.format_exc())
