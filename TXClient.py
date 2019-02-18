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
            running the programs on the Jetson.
        Mode: May be set to a number inclusive of the range -1 to 3. 1 runs with single camera, 2 runs with two 
            in vision processing, 3 solely streams video to SmartDashboard.
        CameraStream: Boolean that can be toggled to True when using a camera on the robot, works with
            _run() and _dualrun().
        Camera: Toggles between cameras (cameraSoleStream only).
'''


class TXClient:

    def __init__(self):

        self.__Table = comms.ConnectTable()
        self.isReset = False
        self.__vidstream = comms.VideoStream()
        self.AsourceStatus = None
        self.BsourceStatus = None

        while self.__Table.Connected:
            self.__Table.table.putBoolean("tableExists", True)

            if self.__Table.table.getNumber("Mode", -1) is 0:
                self._test()

            elif self.__Table.table.getNumber("Mode", -1) is 1:
                self._run()

                self.__avg_centers = []
                self.__all_centers = []
                self.__contour_dimensions = []

            elif self.__Table.table.getNumber("Mode", -1) is 2:
                self._dualrun()

                self.__lavg_centers = []
                self.__lall_centers = []
                self.__lcontour_dimensions = []
                self.__ravg_centers = []
                self.__rall_centers = []
                self.__rcontour_dimensions = []

            elif self.__Table.table.getNumber("Mode", -1) is 3:
                self._cameraSoleStream()

    def _visReset(self):

        """Method to reset variables after finishing loop and be ready for enabling. Reset code goes here."""

        return

    def _cameraSoleStream(self):

        try:
            self.__bvissource
            self.__tvissource

        except NameError:
            try:
                self.__bvissource = bvl.CamLib.cv_video_source('/dev/video1')

            except Exception:
                self.AsourceStatus = False

            else:
                self.AsourceStatus = True

            try:
                self.__tvissource = bvl.CamLib.cv_video_source('/dev/video2')

            except Exception:
                self.BsourceStatus = False

            else:
                self.BsourceStatus = True

        if self.__Table.table.getBoolean("Enabled", False) is True:
            if self.AsourceStatus is True:
                bret, bsource = self.__bvissource.read()

            else:
                bsource = np.zeros((1, 1, 3))

            if self.BsourceStatus is True:
                tret, tsource = self.__tvissource.read()

            else:
                tsource = np.zeros((1, 1, 3))

            if self.__Table.table.getNumber("Camera", 0) is 0:
                self.__vidstream.putFrame(tsource)

            elif self.__Table.table.getNumber("Camera", 0) is 1:
                self.__vidstream.putFrame(bsource)

    def _dualrun(self):

        try:
            self.__lvissource
            self.__rvissource

        except NameError:
            try:
                self.__lvissource = bvl.CamLib.cv_video_source('/dev/video1')

            except Exception:
                self.AsourceStatus = False

            else:
                self.AsourceStatus = True

            try:
                self.__rvissource = bvl.CamLib.cv_video_source('/dev/video2')

            except Exception:
                self.BsourceStatus = False

            else:
                self.BsourceStatus = True

        if self.__Table.table.getBoolean("Enabled", False) is True:
            if self.AsourceStatus is True:
                lret, lsource = self.__lvissource.read()

            else:
                lsource = np.zeros((1, 1, 3))

            if self.BsourceStatus is True:
                rret, rsource = self.__rvissource.read()

            else:
                rsource = np.zeros((1, 1, 3))

            self.__lavg_centers, self.__lall_centers, self.__lcontour_dimensions = src.Src.vision_assistance_contour(lsource)
            self.__ravg_centers, self.__rall_centers, self.__rcontour_dimensions = src.Src.vision_assistance_contour(rsource)
            self.isReset = False

            if len(self.__lcontour_dimensions) > 1:
                self.__lcwidth = abs(self.__lcontour_dimensions[1, 1] - (self.__lcontour_dimensions[0, 1] + self.__lcontour_dimensions[0, 3]))

            elif len(self.__lcontour_dimensions) == 1:
                self.__lcwidth = self.__lcontour_dimensions[0, 3]

            lcenterdist = -(lsource.shape[0]/2 - self.__lavg_centers)
            lhypodist = (lcenterdist*3.5) / self.__lcwidth
            loffset_direction = math.degrees(math.atan(lhypodist / lcenterdist))

            if len(self.__rcontour_dimensions) > 1:
                self.__rcwidth = abs(self.__rcontour_dimensions[1, 1] - (self.__rcontour_dimensions[0, 1] + self.__rcontour_dimensions[0, 3]))

            elif len(self.__rcontour_dimensions) == 1:
                self.__rcwidth = self.__rcontour_dimensions[0, 3]

            rcenterdist = -(rsource.shape[0]/2 - self.__ravg_centers)
            rhypodist = (rcenterdist * 3.5) / self.__rcwidth
            roffset_direction = math.degrees(math.atan(rhypodist / rcenterdist))

            self.__Table.table.putNumber("Left Camera Direction", loffset_direction)
            self.__Table.table.putNumber("Right Camera Direction", roffset_direction)
            self.__Table.table.putNumber("Left Camera Distance", lhypodist)
            self.__Table.table.putNumber("Right Camera Distance", rhypodist)

            if self.__Table.table.getBoolean("CameraStream", False) is True:
                lsource = bvl.RobotVision.rotate_image(lsource, -90, False)
                self.__vidstream.putFrame(lsource)

        elif self.isReset is False and self.__Table.table.getBoolean("Enabled", False) is False:
            self._visReset()
            self.isReset = True

    def _run(self):

        """Single run only. Recommended for flexibility on termination."""

        try:
            self.__vissource

        except NameError:
            try:
                self.__vissource = bvl.CamLib.cv_video_source('/dev/video1')

            except Exception:
                self.AsourceStatus = False

            else:
                self.AsourceStatus = True

        if self.__Table.table.getBoolean("Enabled", False) is True:
            if self.AsourceStatus is True:
                ret, source = self.__vissource.read()

            else:
                source = np.zeros((1, 1, 3))

            self.__avg_centers, self.__all_centers, self.__contour_dimensions = src.Src.vision_assistance_contour(source)
            self.isReset = False

            if len(self.__contour_dimensions) > 1:
                self.__cwidth = abs(self.__contour_dimensions[1, 1] - (self.__contour_dimensions[0, 1] + self.__contour_dimensions[0, 3]))

            elif len(self.__contour_dimensions) == 1:
                self.__cwidth = self.__contour_dimensions[0, 3]

            centerdist = (source.shape[0]/2-self.__avg_centers)
            hypodist = (centerdist*3.5) / self.__cwidth
            offset_direction = math.degrees(math.atan(hypodist/centerdist))

            self.__Table.table.putNumberArray("contour centers", self.__avg_centers)
            self.__Table.table.putNumberArray("all visible contour centers", self.__all_centers)
            self.__Table.table.putNumberArray("all contour dimensions", self.__contour_dimensions)
            self.__Table.table.putNumber("Direction", offset_direction)
            self.__Table.table.putNumber("Camera Distance", hypodist)

            if self.__Table.table.getBoolean("CameraStream", False) is True:
                self.__vidstream.putFrame(source)

        elif self.isReset is False and self.__Table.table.getBoolean("Enabled", False) is False:
            self._visReset()
            self.isReset = True

    def _test(self):

        """Test for connection and enabling"""
        if self.__Table.table.getBoolean("Enabled", False) is True:
            if self.__Table.table.getNumber("Number", 0) is 1:
                self.__Table.table.putNumber("Number", 0)

    '''def looprun(self):

        """Run function looping itself."""

        while self.__Table.Connected:
            self.__Table.table.putBoolean("tableExists", True)

            if self.__Table.table.getBoolean("Enabled", False) is True:

                # Put code here using 'src' package.
    '''


if __name__ == '__main__':
    try:
        TXC = TXClient()
    except Exception as e:
        with open('txclientlog.txt', 'w') as f:
            f.write(str(e))
            f.write(traceback.format_exc())
