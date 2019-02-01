from basicvislib5549 import robotvisionlib

from ntlib import nettable as nt

import numpy as np
import networktables as NetworkTables

'''
    TXClient is the main client that will run on the Jetson TX2.

    Upon running
'''


class TXClient(object):

    def __init__(self):
        self.SmartDash = nt.ConnectTable()

    def run(self):

        '''Single run only. Recommended for flexibility on termination.'''

        if self.SmartDash.Connected:
            self.SmartDash.Table.putBoolean("tableExists", True)

            if self.SmartDash.Table.getBoolean("Enabled", False) is True:

                '''
                Put code here using 'src' package.
                '''

    def looprun(self):

        '''Run function looping itself.'''

        while self.SmartDash.Connected:
            self.SmartDash.Table.putBoolean("tableExists", True)

            if self.SmartDash.Table.getBoolean("Enabled", False) is True:

                '''
                Put code here using 'src' package.
                '''


if __name__ == '__main__':
    TXC = TXClient()

    while True:
        TXC.run()