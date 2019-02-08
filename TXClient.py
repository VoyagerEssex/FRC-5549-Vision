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

        self.Table = ntlib.ConnectTable().table
        self.vis_init()
        self.isReset = False

        while self.Table.Connected:
            self.Table.putBoolean("tableExists", True)

            if self.Table.getNumber("Mode", -1) is 0:
                self.test()

            elif self.Table.getNumber("Mode", -1) is 1:
                self.run()

    def vis_init(self):

        self.source = bvl.CamLib.cv_video_source('/dev/video1')

        self.avg_centers = []
        self.all_centers = []
        self.contour_dimensions = []

    def vis_reset(self):

        """Method to reset variables after finishing loop and be ready for enabling. Reset code goes here."""

        return

    def run(self):

        """Single run only. Recommended for flexibility on termination."""

        if self.Table.getBoolean("Enabled", False) is True:
            self.avg_centers, self.all_centers, self.contour_dimensions = src.Src.vision_assistance_contour(self.source)
            self.isReset = False

            self.Table.putNumberArray("contour centers", self.avg_centers)

            self.Table.putNumberArray("all visible contour centers", self.all_centers)

            self.Table.putNumberArray("all contour dimensions", self.contour_dimensions)

        elif self.isReset is False and self.Table.getBoolean("Enabled", False) is False:
            self.vis_reset()
            self.isReset = True

    def test(self):

        """Test for connection and enabling"""
        if self.Table.getBoolean("Enabled", False) is True:
            if self.Table.getNumber("Number", 0) is 1:
                self.Table.putNumber("Number", 0)

    '''def looprun(self):

        """Run function looping itself."""

        while self.Table.Connected:
            self.Table.table.putBoolean("tableExists", True)

            if self.Table.table.getBoolean("Enabled", False) is True:

                # Put code here using 'src' package.
    '''


if __name__ == '__main__':
    TXC = TXClient()
