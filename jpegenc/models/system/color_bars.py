
import myhdl

from .interfaces import RGBStream
from .video_source import VideoSource


class ColorBars(VideoSource):
    def __init__(self, resolution=(1920, 1080), color_depth=(8, 8, 8),
                 frame_rate=60, swap_rate=1):
        """

        Args:
            resolution (tuple):
            color_depth (tuple):
            frame_rate (float): frame rate of the video in Hz
            swap_rate  (float): color bar shift in Hz
                swap_rate:
        """
        self.resolution = resolution
        self.color_depth = color_depth
        self.frame_rate = frame_rate
        self.swap_rate = swap_rate
        super(ColorBars, self).__init__(resolution, frame_rate)

    @myhdl.block
    def process(self, glbl):
        """Generate a color bar video stream

        Args:
            clock (SignalType): system clock
            pixels (RGBStream): pixel stream

        not convertible
        """
        clock = glbl.clock
        pixels = self.pixels

    def check_pixel(self, buffer, frame=0):
        """Regenerate a frame and compare it to a buffer

        Args:
            frame (int): which frame to compare

        Returns:

        """