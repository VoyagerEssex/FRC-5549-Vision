from enum import IntEnum

class PlatformType(IntEnum):
    USB_CAM_LINUX = 1
    USB_CAM_WIN = 2
    JETSON_TX2_INT = 3

class BlurType(IntEnum):
    Box_Blur = 1
    Gaussian_Blur = 2
    Median_Filter = 3