from enum import IntEnum

class PlatformType(IntEnum):
    USB_CAM_LINUX = 1
    USB_CAM_WIN = 2
    JETSON_TX2_INT = 3

class BlurType(IntEnum):
    BOX_BLUR = 1
    GAUSSIAN_BLUR = 2
    MEDIAN_FILTER = 3