import numpy as np
import cscore as cs
import logging

"""
Class creates a server which streams video to a sink or server. In this case,
OpenCV frames by calling 'putFrame' in TXClient.
"""


class VideoStream:
    Instances = 0

    def __init__(self):
        try:
            logging.basicConfig(level=logging.DEBUG)
            self.streamFailure = None
            self._source = cs.CvSource(("video%d" % VideoStream.Instances), cs.VideoMode.PixelFormat.kMJPEG)

        except Exception:
            self.streamFailure = True

        else:
            self.streamFailure = False
            VideoStream._iterInstances()

    def putFrame(self, cv_frame: np.ndarray):
        self._source.putFrame(cv_frame)

    @classmethod
    def _iterInstances(cls):
        cls.Instances += 1
