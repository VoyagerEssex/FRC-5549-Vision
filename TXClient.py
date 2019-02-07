import basicvislib5549 as bvl
import ntlib
import src

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

        while self.Table.Connected:
            self.Table.table.putBoolean("tableExists", True)

            if self.Table.table.getNumber("Mode", -1) is 0:
                self.test()

            elif self.Table.table.getNumber("Mode", -1) is 1:
                self.run()

    def vis_init(self):

        self.lsource = bvl.CamLib.cv_video_source('/dev/video1')
        self.rsource = bvl.CamLib.cv_video_source('/dev/video2')

        self.lavg_centers = []
        self.lall_centers = []
        self.lcontour_dimensions = []
        
        self.ravg_centers = []
        self.rall_centers = []
        self.rcontour_dimensions = []

    def vis_reset(self):

        """Method to reset variables after finishing loop and be ready for enabling. Reset code goes here."""

        return

    def run(self):

        """Single run only. Recommended for flexibility on termination."""

        if self.Table.table.getBoolean("Enabled", False) is True:
            self.avg_centers, self.all_centers, self.contour_dimensions = src.Src.vision_assistance_contour(self.lsource)
            self.avg_centers, self.all_centers, self.contour_dimensions = src.Src.vision_assistance_contour(self.rsource)
            self.isReset = False

            self.Table.table.putNumberArray("left camera contour centers", self.lavg_centers)
            self.Table.table.putNumberArray("left camera visible contour centers", self.lall_centers)
            self.Table.table.putNumberArray("left camera contour dimensions", self.lcontour_dimensions)
            
            self.Table.table.putNumberArray("right camera contour centers", self.ravg_centers)
            self.Table.table.putNumberArray("right camera visible contour centers", self.rall_centers)
            self.Table.table.putNumberArray("right camera contour dimensions", self.rcontour_dimensions)

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
