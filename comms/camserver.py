import numpy as np
import cscore as cs

"""
Class creates a server which streams video to a sink or server. In this case,
OpenCV frames by calling 'putFrame' in TXClient.
"""


class VideoStream:
    Instances = 0

    def __init__(self):
        self._sink = cs.MjpegServer("DS", 8083)
        self._source = cs.CvSource(("video%d" % VideoStream.Instances), cs.VideoMode.PixelFormat.kMJPEG)
        self._sink.setSource(self._source)
        VideoStream.Instances += 1

    def putFrame(self, cv_frame: np.ndarray):
        self.source.putFrame(cv_frame)
